{pkgs ? import <nixpkgs> {}, python ? pkgs.python34, pythonPackages ? pkgs.python34Packages}:
pythonPackages.buildPythonPackage {
  name = "reqtxt2nix-git";
  src = ./.;
  buildInputs = [ pythonPackages.pip ];
  meta = {
    description = "The pythonic requirements.txt to nix environment converter";
    maintainers = [ "Paul Colomiets <paul@colomiets.name>" ];
    license = "MIT";
  };
}
