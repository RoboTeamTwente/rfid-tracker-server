{ inputs, cell }:
let
  inherit (inputs) nixpkgs;
  inherit (inputs.std) lib;

  l = builtins // nixpkgs.lib;
in
{

  treefmt = lib.dev.mkNixago lib.cfg.treefmt {
    packages = [
      nixpkgs.djhtml
      nixpkgs.libxml2 # xmllint
      nixpkgs.nixfmt
      nixpkgs.prettier
      nixpkgs.ruff
      nixpkgs.taplo
    ];
    data = {
      global = {
        on-unmatched = "warn";
        excludes = [ "CHANGELOG.md" ];
      };
      formatter = {
        djhtml = {
          command = "djhtml";
          includes = [ "**/templates/**.html" ];
        };
        nixfmt = {
          command = "nixfmt";
          includes = [ "*.nix" ];
        };
        prettier = {
          command = "prettier";
          options = [ "--write" ];
          includes = [
            "*.css"
            "*.html"
            "*.json"
            "*.md"
            "*.yaml"
          ];
          excludes = [ "**/templates/**.html" ];
        };
        ruff-check = {
          command = "ruff";
          options = [
            "check"
            "--fix"
          ];
          includes = [ "*.py" ];
        };
        ruff-format = {
          command = "ruff";
          options = [ "format" ];
          includes = [ "*.py" ];
        };
        taplo = {
          command = "taplo";
          options = [ "format" ];
          includes = [ "*.toml" ];
        };
        xmllint = {
          command = "xmllint";
          options = [ "--format" ];
          includes = [ "*.svg" ];
        };
        shellcheck = {
          command = "shellcheck";
          includes = [ "*.sh" ];
        };
      };
    };
  };

  lefthook = lib.dev.mkNixago lib.cfg.lefthook {
    packages = [
      nixpkgs.actionlint
      nixpkgs.ripsecrets
      nixpkgs.shellcheck # used by actionlint
    ];
    data = {
      pre-push = {
        parallel = true;
        commands = {
          cocogitto.run = ''
            set -ex
            read -r local_ref local_sha remote_ref remote_sha
            if [ "$remote_sha" = 0000000000000000000000000000000000000000 ]
            then remote_sha=main
            fi
            cog check "$remote_sha..$local_sha"
          '';
        };
      };
      pre-commit = {
        parallel = true;
        fail_on_changes = "ci"; # only when $CI=1
        commands = {
          actionlint = {
            run = "actionlint '{staged_files}'";
            glob = ".github/workflows/*.yaml";
          };
          ripsecrets = {
            run = "ripsecrets --strict-ignore '{staged_files}'";
            file_types = [ "text" ];
          };
          treefmt = {
            run = "treefmt '{staged_files}'";
            stage_fixed = true;
          };
          django-make-migrations.run = "just django makemigrations --check";
          django-test.run = "just test";
        };
      };
    };
  };

}
