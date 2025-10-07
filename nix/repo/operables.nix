{ inputs, cell }:
let
  inherit (inputs) nixpkgs;
  inherit (inputs.std) lib;

  l = builtins // nixpkgs.lib;

in
{
  serve = lib.ops.mkOperable {
    package = cell.packages.venv;
    runtimeScript = ''
      admin migrate
      admin init_admin
      daphne -b 0.0.0.0 door_tracker.asgi:application
    '';
    runtimeEnv = {
      DJANGO_STATIC_ROOT = cell.packages.static;
    };
    runtimeInputs = [
      cell.packages.admin
      cell.packages.init
      cell.packages.venv
    ];
    debugInputs = [
      nixpkgs.sqlite
    ];
  };
}
