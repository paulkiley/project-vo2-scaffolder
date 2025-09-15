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

