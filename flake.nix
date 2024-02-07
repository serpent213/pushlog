# Run
#
#   nix develop
#
# to run development shell.

{
  description = "systemd journal to Pushover";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.11";
    # or for unstable
    # nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonPatched = (pkgs.python311.override {
        packageOverrides = pyfinal: pyprev: {};
      }).withPackages(pp: with pp; [
        click
        fuzzywuzzy
        pyyaml
        systemd
      ]);
      buildInputs = with pkgs; [
        pythonPatched
      ];
    in {
      devShells.default = pkgs.mkShell {
        inherit buildInputs;
      };
    });
}
