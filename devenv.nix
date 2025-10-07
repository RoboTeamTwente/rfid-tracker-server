{
  config,
  inputs,
  lib,
  pkgs,
  ...
}@args:

let
  venv = import ./python.nix args;
in

{

  ## Scripts

  scripts.django.exec = ''
    cd "$DEVENV_ROOT/door_tracker"
    uv run manage.py "$@"
  '';

  scripts.dev.exec = ''
    django migrate &&
    django runserver "$@"
  '';

  scripts.makemigrations.exec = ''
    django makemigrations "$@"
  '';

  scripts.migrate.exec = ''
    django migrate "$@"
  '';

  scripts.init.exec = ''
    django migrate &&
    django createsuperuser "$@"
  '';

  scripts.repl.exec = ''
    django shell "$@"
  '';

  scripts.current-version.exec = ''
    cd "$DEVENV_ROOT/door_tracker"
    cz version -p
  '';

  scripts.bump-version.exec = ''
    cd "$DEVENV_ROOT"
    if ! git diff --quiet
    then
    	echo Dirty worktree, aborting
    	exit 1
    fi
    if ! git rev-parse --abbrev-ref @ | grep -qx main
    then
    	echo Not on main branch, aborting
    	exit 1
    fi
    git fetch
    if test "$(git rev-list --count refs/heads/main..refs/remotes/origin/main)" != 0
    then
    	echo main branch out of sync, aborting
    	exit 1
    fi
    cleanup() {
    	# remove temporary changelog file if it exists
    	test -f "''${changelog-}" && rm "''${changelog-}"
    }
    trap cleanup EXIT
    set -eux
    cd "$DEVENV_ROOT"
    devenv test
    cd "$DEVENV_ROOT/door_tracker"
    changelog="$(mktemp)"
    tag="v$(cz bump --get-next)"
    cz bump --yes --retry --changelog-to-stdout --git-output-to-stderr > "$changelog"
    git push origin main "$tag"
    gh release create "$tag" --notes-file "$changelog"
  '';

  scripts.docker-login.exec = ''
    skopeo login docker.io -u roboteamtwente "$@"
  '';

  scripts.build-container.exec = ''
    set -eu
    name=$1; shift
    set -x
    cd "$DEVENV_ROOT"
    $(devenv build --refresh-eval-cache outputs.containers."$name".copyToDockerDaemon)/bin/copy-to-docker-daemon "$@"
  '';

  scripts.upload-container.exec = ''
    set -eu
    name=$1; shift
    set -x
    cd "$DEVENV_ROOT"
    $(devenv build --refresh-eval-cache outputs.containers."$name".copyToRegistry)/bin/copy-to-registry "$@"
  '';

  scripts.upload-container-to.exec = ''
    set -eu
    name=$1; shift
    set -x
    cd "$DEVENV_ROOT"
    $(devenv build --refresh-eval-cache outputs.containers."$name".copyTo)/bin/copy-to "$@"
  '';

  scripts.deliver.exec =
    let
      destination = lib.escapeShellArg "docker://${lib.escapeShellArg config.outputs.containers.serve.imageName}";
    in
    ''
      set -eux
      cd "$DEVENV_ROOT"
      version=$(current-version)
      "$(devenv build --refresh-eval-cache outputs.containers.serve.copyTo)"/bin/copy-to ${destination}:"$version"
      skopeo --insecure-policy copy ${destination}:"$version" ${destination}:"$(echo "$version" | cut -d. -f-2)"
      skopeo --insecure-policy copy ${destination}:"$version" ${destination}:"$(echo "$version" | cut -d. -f-1)"
      skopeo --insecure-policy copy ${destination}:"$version" ${destination}:latest
    '';

  scripts.release.exec = ''
    set -eux
    bump-version
    deliver
  '';

  ## Languages

  languages.python = {
    enable = true;
    uv.enable = true;
    uv.sync.enable = true;
    directory = "door_tracker";
  };

  enterShell = ''
    export PATH="$UV_PROJECT_ENVIRONMENT/bin''${PATH+:}$PATH"
  '';

  ## Extra packages

  packages = [
    pkgs.commitizen
    pkgs.curl
    pkgs.djhtml
    pkgs.doxygen
    pkgs.git
    pkgs.httpie
    pkgs.openssh
    pkgs.skopeo
  ];

  ## Tests

  tasks."django:test" = {
    exec = "django test";
    before = [ "devenv:enterTest" ];
  };

  ## Packages

  outputs.packages = {
    admin = pkgs.writeShellApplication {
      name = "admin";
      runtimeInputs = [ venv ];
      text = ''
        DJANGO_SETTINGS_MODULE=door_tracker.settings django-admin "$@"
      '';
    };

    static = pkgs.stdenv.mkDerivation {
      name = "static";
      src = ./door_tracker;

      dontConfigure = true;
      dontBuild = true;

      nativeBuildInputs = [ config.outputs.packages.admin ];

      installPhase = ''
        DJANGO_STATIC_ROOT=$out admin collectstatic --no-input
      '';
    };

    serve = pkgs.writeShellApplication {
      name = "serve";
      runtimeInputs = [
        config.outputs.packages.admin
        venv
      ];
      runtimeEnv.DJANGO_STATIC_ROOT = config.outputs.packages.static;
      text = ''
        admin migrate
        admin init_admin
        daphne -b 0.0.0.0 door_tracker.asgi:application
      '';
    };

    init = pkgs.writeShellApplication {
      name = "init";
      runtimeInputs = [ config.outputs.packages.admin ];
      text = ''
        admin migrate
        admin createsuperuser
      '';
    };
  };

  ## Containers

  outputs.containers = {
    serve = inputs.nix2container.packages.${pkgs.system}.nix2container.buildImage {
      name = "roboteamtwente/rfid-tracker-serve";
      tag = "latest";
      maxLayers = 16; # max 125
      copyToRoot = [
        config.outputs.packages.admin
        config.outputs.packages.init
        config.outputs.packages.serve
        pkgs.sqlite
        pkgs.tini
      ];
      config.Cmd = [
        "/bin/tini"
        "/bin/serve"
      ];
    };
  };

  ## Config files

  files.".vscode/tasks.json".json = {
    # See https://go.microsoft.com/fwlink/?LinkId=733558
    # for the documentation about the tasks.json format
    version = "2.0.0";
    tasks =
      # scripts
      lib.mapAttrsToList
        (
          name: _:
          {
            label = "run script: ${name}";
            type = "shell";
            command = name;
            group = "build";
          }
          // lib.optionalAttrs (name == "dev") {
            group.kind = "build";
            group.isDefault = name == "dev";
            runOptions.runOn = "folderOpen";
          }
        )
        (
          lib.removeAttrs config.scripts [
            "build-container"
            "django"
            "upload-container"
          ]
        )
      # containers
      ++ lib.concatMap (name: [
        {
          label = "build container: ${name}";
          type = "shell";
          command = "$(devenv build outputs.containers.${lib.escapeShellArg name}.copyToDockerDaemon)/bin/copy-to-docker-daemon";
          group = "build";
        }
        {
          label = "upload container: ${name}";
          type = "shell";
          command = "$(devenv build outputs.containers.${lib.escapeShellArg name}.copyToRegistry)/bin/copy-to-registry";
          group = "build";
        }
      ]) (lib.attrNames config.outputs.containers)
      # packages
      ++ lib.mapAttrsToList (name: _: {
        label = "build package: ${name}";
        type = "shell";
        command = "devenv build outputs.packages.${lib.escapeShellArg name}";
        group = "build";
      }) config.outputs.packages;
  };

  ## Git hooks

  git-hooks.hooks = {
    actionlint.enable = true;
    check-executables-have-shebangs.enable = true;
    check-json.enable = true;
    check-merge-conflicts.enable = true;
    check-shebang-scripts-are-executable.enable = true;
    check-symlinks.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;
    commitizen.enable = true;
    deadnix.enable = true;
    detect-private-keys.enable = true;
    eclint.enable = true;
    end-of-file-fixer.enable = true;
    eslint.enable = true;
    fix-byte-order-marker.enable = true;
    hadolint.enable = true;
    markdownlint.enable = true;
    nixfmt-rfc-style.enable = true;
    ripsecrets.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    taplo.enable = true;
    trim-trailing-whitespace.enable = true;
    uv-check.enable = true;
  };

  git-hooks.hooks.djhtml = {
    enable = true;
    entry = "djhtml";
    files = ''templates/.*\.html$'';
  };

  git-hooks.hooks.makemigrations = {
    enable = true;
    entry = "makemigrations";
    args = [
      "--no-input"
      "--check"
    ];
    always_run = true;
    pass_filenames = false;
  };

  git-hooks.hooks.django-test = {
    enable = true;
    entry = "django test";
    always_run = true;
    pass_filenames = false;
  };

  git-hooks.hooks.prettier = {
    enable = true;
    excludes = [ ''templates/.*\.html$'' ];
  };

}
