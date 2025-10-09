{ inputs, cell }:
let
  inherit (inputs) nixpkgs;
  inherit (inputs.std) lib;

  l = builtins // nixpkgs.lib;

  inherit (cell.packages.roboteam-door-tracker) version;

  truncVersion =
    level:
    l.pipe version [
      l.splitVersion
      (l.take level)
      (l.concatStringsSep ".")
    ];

  baseConfig = {
    name = "roboteamtwente/rfid-tracker-serve";
    operable = cell.operables.serve;
    debug = true;
    uid = "0"; # who cares about security, right?
    labels = {
      inherit version;
      commit = inputs.self.shortRev or inputs.self.dirtyShortRev;
    };
  };

in
{

  dev = lib.ops.mkStandardOCI (baseConfig // { tag = "latest"; });

  prod-major = lib.ops.mkStandardOCI (baseConfig // { tag = truncVersion 1; });
  prod-minor = lib.ops.mkStandardOCI (baseConfig // { tag = truncVersion 2; });
  prod-patch = lib.ops.mkStandardOCI (baseConfig // { tag = truncVersion 3; });
  prod-latest = lib.ops.mkStandardOCI (baseConfig // { tag = "latest"; });

}
