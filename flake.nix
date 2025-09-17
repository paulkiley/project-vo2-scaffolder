{
  description = "Project VO2 Scaffolder – reproducible dev shell via Nix flakes";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
    in {
      devShells = forAllSystems (pkgs: let
        py = pkgs.python311;
        pyWith = pkgs.python311.withPackages (ps: with ps; [
          pyyaml
          jsonschema
          jinja2
          pip
          setuptools
          wheel
        ]);
      in {
        default = pkgs.mkShell {
          packages = with pkgs; [
            git
            just
            jq
            yq
            ripgrep
            nox
            ruff
            black
            poetry
            pyWith
            pipx
            shellcheck
          ];
          shellHook = ''
            echo "[nix] Dev shell ready: just, nox, ruff, python(+pyyaml+jsonschema)"
          '';
        };
      });

      formatter = forAllSystems (pkgs: pkgs.nixpkgs-fmt);

      checks = forAllSystems (pkgs: {
        python-deps = pkgs.runCommand "python-deps" { buildInputs = [ (pkgs.python311.withPackages (ps: with ps; [ pyyaml jsonschema ])) ]; } ''
          python - <<'PY'
          import yaml, jsonschema; print('ok')
          PY
          touch $out
        '';
      });
    };
}
