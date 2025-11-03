{
  # std
  inputs = {
    arion.url = "github:hercules-ci/arion";
    devshell.url = "github:numtide/devshell";
    n2c.url = "github:nlewo/nix2container";
    nixago.url = "github:nix-community/nixago";
    nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.xz";
    std = {
      inputs.arion.follows = "arion";
      inputs.devshell.follows = "devshell";
      inputs.n2c.follows = "n2c";
      inputs.nixago.follows = "nixago";
      url = "github:divnix/std";
    };
    pyproject-build-systems = {
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      url = "github:pyproject-nix/build-system-pkgs";
    };
    pyproject-nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:pyproject-nix/pyproject.nix";
    };
    uv2nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      url = "github:pyproject-nix/uv2nix";
    };
  };

  outputs =
    inputs:
    inputs.std.growOn
      {
        inherit inputs;
        systems = [
          "x86_64-linux"
          "aarch64-linux"
        ];
        cellsFrom = ./nix;
        cellBlocks = with inputs.std.blockTypes; [
          (containers "containers")
          (devshells "shells" { ci.build = true; })
          (installables "ci-jobs" { ci.build = true; })
          (installables "packages" { ci.build = true; })
          (nixago "dotfiles")
          (runnables "operables" { ci.build = true; })
        ];
      }
      {
        devShells = inputs.std.harvest inputs.self [
          "repo"
          "shells"
        ];
        packages = inputs.std.harvest inputs.self [
          "repo"
          "packages"
        ];
        hydraJobs = inputs.std.harvest inputs.self [
          "repo"
          "ci-jobs"
        ];
      };
}
