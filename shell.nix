{
  sources ? import ./npins { },
  system ? builtins.currentSystem,
  nixpkgs ? import sources.nixpkgs { inherit system; },
  treefmt-nix ? import sources.treefmt-nix,
}:

let

  treefmt = treefmt-nix.mkWrapper nixpkgs {

    settings.global = {
      on-unmatched = "warn";
      excludes = [ "CHANGELOG.md" ];
    };

    settings.formatter = {
      ruff-check.options = [
        "--ignore"
        "RUF012"
      ];
      zizmor.options = [ "--fix" ];
    };

    programs = {
      # keep-sorted start
      actionlint.enable = true;
      clang-format.enable = true;
      deadnix.enable = true;
      dos2unix.enable = true;
      keep-sorted.enable = true;
      nixfmt.enable = true;
      ruff-check.enable = true;
      ruff-format.enable = true;
      rumdl-format.enable = true;
      shellcheck.enable = true;
      shfmt.enable = true;
      statix.enable = true;
      xmllint.enable = true;
      yamlfmt.enable = true;
      zizmor.enable = true;
      # keep-sorted end
    };

  };

in

nixpkgs.mkShellNoCC {
  packages = [
    # keep-sorted start
    treefmt
    # keep-sorted end
  ];
}
