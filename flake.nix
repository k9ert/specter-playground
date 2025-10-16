{
  description = "Specter DIY development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [
            pkgs.buildPackages.gcc-arm-embedded
            pkgs.buildPackages.python3
            pkgs.openocd
            pkgs.SDL2
          ] ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
            pkgs.stlink  # stlink is not supported on macOS
          ];
          hardeningDisable = ["all"];
        };
      });
}
