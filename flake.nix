# Run
#
#   nix develop
#
# to run development shell.
{
  description = "systemd journal to Pushover devshell";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-24.11";
    # or for unstable
    # nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonPatched = pkgs.python3.withPackages (pp:
        with pp; [
          # Runtime dependencies
          click
          fuzzywuzzy
          pyyaml
          systemd
          
          # Development dependencies
          pytest
          pytest-cov
          flake8
        ]);
      buildInputs = [
        pythonPatched
      ];
    in {
      devShells.default = pkgs.mkShell {
        inherit buildInputs;
      };
    });
}
