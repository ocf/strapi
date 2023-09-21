{
  description = "A very basic flake";

  inputs = {
    transpire.url = "github:ocf/transpire";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, transpire, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ transpire.packages.${system}.default ];
        };
        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
