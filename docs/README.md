# Project VO2 Scaffolder — Documentation

This repository provides a professional, reproducible scaffolding system for Project VO2 and similar projects. It generates a complete project workspace, validates integrity, and renders documentation/templates.

- Source of truth: commit-time files under `src/project_vo2_scaffolder/data_files` and adjacent Python/shell sources
- Derived artifact: `file_contents.jsonl` manifest (deterministically built via `populate.sh`)
- Materialization: `02-populate-files.py` writes files to the current directory, verifying checksums and permissions
- Rendering: `render.py` processes Jinja2 templates (`.j2`) with a YAML/JSON context
- Task runner: `Justfile` provides ergonomics; `nox` validates manifests; `copier` supports template application

See ADRs in `docs/adr/` for rationale and tradeoffs.

## Quickstart

- Build manifest: `just db`
- Validate manifest: `just validate`
- Populate files into CWD: `just populate`
- Verify no drift vs sources: `just verify`
- Render docs/templates: `just render CONTEXT=project-vo2-scaffolder/copier-defaults.yaml OUT=./rendered`
- Strict rendering (fail on missing vars): `just render-strict CONTEXT=my-context.yaml`
- Copy template via Copier: `just copier DEST=../my-new-project`

## Layout

- `src/project_vo2_scaffolder/data_files/` — canonical scaffold content (scripts, templates, docs, configs)
- `populate.sh` — builds `file_contents.jsonl` (base64, checksums, size, mode)
- `02-populate-files.py` — materializes files, enforces integrity and path safety
- `render.py` — renders `.j2` templates with provided context (YAML/JSON)
- `noxfile.py` — `validate_manifest` session for CI/local validation
- `Justfile` — convenient targets for common operations
- `docs/adr/` — architecture decisions
- `examples/` — contexts and command examples

## CI Suggestions

- GitHub Actions CI runs on pushes and pull requests:
  - Validate manifest: `nox -s validate_manifest`
  - Verify manifest matches sources: `bash verify.sh`
  - Render default docs and upload as an artifact
- Release workflow (on tags like `vX.Y.Z`) publishes:
  - `file_contents.jsonl`
  - `data_files.zip`
  - `rendered-docs-default.zip`
  - `CHECKSUMS.txt`
