# Project VO2 Scaffolder

[![CI](https://github.com/paulkiley/project-vo2-scaffolder/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/paulkiley/project-vo2-scaffolder/actions/workflows/ci.yml)
[![Release Please](https://github.com/paulkiley/project-vo2-scaffolder/actions/workflows/release-please.yml/badge.svg)](https://github.com/paulkiley/project-vo2-scaffolder/actions/workflows/release-please.yml)
[![GitHub release](https://img.shields.io/github/v/release/paulkiley/project-vo2-scaffolder?sort=semver)](https://github.com/paulkiley/project-vo2-scaffolder/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint: ruff](https://img.shields.io/badge/lint-ruff-46a2f1)](https://github.com/astral-sh/ruff)
[![Security: gitleaks](https://img.shields.io/badge/security-gitleaks-red)](https://github.com/gitleaks/gitleaks)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-orange.svg)](https://www.conventionalcommits.org/en/v1.0.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

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
