# Project VO2 Scaffolder

Professional, reproducible scaffolding for Project VO2. Generates a complete workspace, validates integrity, and renders documentation/templates.

- Source of truth: `src/project_vo2_scaffolder/data_files/`
- Derived artifact: `file_contents.jsonl` (via `populate.sh`)
- Materialization: `02-populate-files.py`
- Rendering: `render.py` (Jinja2) or Copier
- Tasks: `Justfile`; Validation: `nox`; CI: GitHub Actions

## Quickstart

- Build manifest: `just db`
- Validate: `just validate`
- Verify drift: `just verify`
- Populate files: `just populate`
- Render templates: `just render CONTEXT=examples/context-minimal.yaml OUT=./rendered`

## Docs
- Contributing: see [CONTRIBUTING.md](CONTRIBUTING.md)
- Security policy: see [SECURITY.md](SECURITY.md)
- Overview docs: [docs/README.md](docs/README.md)
- ADRs: [docs/adr](docs/adr)
