{ inputs, cell }:
let
  inherit (inputs) nixpkgs;
  inherit (inputs.std.lib.dev) mkShell;
  inherit (inputs.std) std;

  l = builtins // nixpkgs.lib;
in
nixpkgs.lib.mapAttrs (_: mkShell) {
  default = {
    name = "RFiD Tracker";
    imports = [
      std.devshellProfiles.default
    ];
    packages = [
      nixpkgs.curl
      nixpkgs.doxygen
      nixpkgs.git
      nixpkgs.koji
      nixpkgs.openssh
      nixpkgs.python3
      nixpkgs.skopeo
      nixpkgs.uv
    ];
    commands = [
      { package = nixpkgs.just; }
      { package = nixpkgs.xh; }
    ];
    nixago = [
      cell.dotfiles.lefthook
      cell.dotfiles.treefmt
    ];
    env = [
      {
        name = "UV_PROJECT";
        eval = "$PRJ_ROOT/door_tracker";
      }
      {
        name = "PATH";
        prefix = "$PRJ_ROOT/door_tracker/.venv/bin";
      }
    ];
  };
}
