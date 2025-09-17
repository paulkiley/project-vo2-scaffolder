# Repository Setup (Scaffolder)

This document describes project‑scoped setup steps that are safe to keep in Git. It does not include personal machine paths or private content.

## Initialize Git and push

```
# From repo root
git init
git add -A
git commit -m "init: project-vo2 scaffolder"
# Create a GitHub repo named project-vo2-scaffolder, then:
git remote add origin git@github.com:<your-user>/project-vo2-scaffolder.git
git branch -M main
git push -u origin main
```

## CI and releases

- CI: `.github/workflows/ci.yml` validates the manifest, verifies drift, and uploads rendered docs as an artifact.
- Releases: `.github/workflows/release.yml` runs on tags like `vX.Y.Z` and publishes:
  - `file_contents.jsonl`
  - `manifest_meta.json`
  - `data_files.zip`
  - optional `rendered-docs-default.zip`
  - `CHECKSUMS.txt`

## Local tasks

Use `just` to run common tasks:

```
just           # list tasks
just db        # build manifest
just validate  # nox validation
just verify    # rebuild and diff manifest
just populate  # write files to CWD
just render CONTEXT=examples/context-minimal.yaml OUT=./rendered
```

## Publishing (optional)

- Build package: `just build-pypi`
- TestPyPI upload: `export TEST_PYPI_API_TOKEN=... && just publish-testpypi`

## Nix Quickstart

We provide a reproducible development environment using Nix flakes. This removes setup drift and ensures required tools are available (just, jq, yq, ripgrep, python with pyyaml+jsonschema, nox, ruff, black, poetry, etc.).

Prerequisites:

- Install Nix: https://nixos.org/download (multi-user recommended)
- Optional: Install direnv and nix-direnv for automatic activation.

Usage:

1) If using direnv:

   - Run `direnv allow` once at the repo root. `.envrc` uses `use flake` to activate the dev shell.

2) Without direnv:

   - Run `nix develop` to enter the dev shell. Exit with Ctrl-D.

Verification:

- `just nix-info` prints Nix version and flake info.
- `just nix-check` runs `nix flake check` to validate the configuration.

Notes:

- Python in the dev shell already includes `pyyaml` and `jsonschema`, so `python3 scripts/work.py validate` will run without extra installation.
- If you don’t have `just` installed globally, use `nix develop -c just <target>`.

