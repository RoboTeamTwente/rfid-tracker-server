{ inputs, cell }:
let
  inherit (inputs) nixpkgs;
  inherit (inputs.std) lib;

  l = builtins // nixpkgs.lib;

  python = nixpkgs.python3;

  workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = inputs.self + /door_tracker;
  };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  # hacks = nixpkgs.callPackage inputs.pyproject-nix.build.hacks { };
  pyprojectOverrides = _pypkgs: _prev: {
  };

  baseSet = nixpkgs.callPackage inputs.pyproject-nix.build.packages { inherit python; };
  pythonSet = baseSet.overrideScope (
    l.composeManyExtensions [
      inputs.pyproject-build-systems.overlays.default
      overlay
      pyprojectOverrides
    ]
  );

in
{
  inherit python;
  inherit (pythonSet) roboteam-door-tracker;

  venv = pythonSet.mkVirtualEnv "rfid-tracker-venv" workspace.deps.default;

  static = nixpkgs.stdenv.mkDerivation {
    name = "static";
    src = inputs.self + /door_tracker;

    dontConfigure = true;
    dontBuild = true;

    nativeBuildInputs = [ cell.packages.admin ];

    installPhase = ''
      DJANGO_STATIC_ROOT=$out admin collectstatic --no-input
    '';
  };

  admin = nixpkgs.writeShellApplication {
    name = "admin";
    runtimeInputs = [ cell.packages.venv ];
    text = ''
      DJANGO_SETTINGS_MODULE=door_tracker.settings django-admin "$@"
    '';
  };

  init = nixpkgs.writeShellApplication {
    name = "init";
    runtimeInputs = [ cell.packages.admin ];
    text = ''
      admin migrate
      admin createsuperuser
    '';
  };
}
