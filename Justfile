# Project VO2 Scaffolder tasks (requires: bash, python3, jq, nox, copier)

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Default target: show available commands
default:
  @just --list

# Create empty directory structure and placeholder files
create-structure:
  bash ./01-create-structure.sh

# Build JSONL database from canonical repo files (uses jq + base64)
db:
  bash ./populate.sh

# Populate files from file_contents.jsonl into the current directory
populate:
  python3 ./02-populate-files.py

# End-to-end: structure -> db -> populate
e2e:
  just create-structure
  just db
  just populate

# Validate manifest with nox (JSON + base64 sanity checks)
validate:
  nox -s validate_manifest

# Render the Copier template into DEST
# Usage: just copier DEST=../my-new-project
copier DEST:
  copier copy --force . "{{DEST}}"

# Verify manifest matches repo sources (rebuild to temp and diff)
verify:
  bash ./verify.sh

# Work ledger helpers
work-list:
  python3 ./scripts/work.py list

work-validate:
  python3 ./scripts/work.py validate

context:
  bash ./scripts/context_bundle.sh

# Render Jinja2 templates into OUT (defaults to CWD)
# Usage: just render CONTEXT=path/to/context.yaml [OUT=./dist] [IN=./templates]
render CONTEXT OUT?=.: IN?=./src/project_vo2_scaffolder/data_files/templates:
  python3 ./render.py --context "{{CONTEXT}}" --out-dir "{{OUT}}" --in-dir "{{IN}}"

# Strict rendering (fail on missing vars)
render-strict CONTEXT OUT?=.: IN?=./src/project_vo2_scaffolder/data_files/templates:
  python3 ./render.py --strict --context "{{CONTEXT}}" --out-dir "{{OUT}}" --in-dir "{{IN}}"

# Build Python package (sdist/wheel) into dist/
build-pypi:
  python -m pip install --upgrade build
  python -m build

# Publish to TestPyPI using environment token
# Usage: export TEST_PYPI_API_TOKEN=...; just publish-testpypi
publish-testpypi:
  python -m pip install --upgrade twine
  TWINE_USERNAME=__token__ TWINE_PASSWORD=${TEST_PYPI_API_TOKEN:?Set TEST_PYPI_API_TOKEN} \
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Show the Agent Onboarding & Operations Manual directive JSONL
show-onboarding-directive:
  cat ./.agent_workdir/directives/onboarding_and_operations_manual.jsonl

# Nix helpers
nix-info:
  if ! command -v nix >/dev/null 2>&1; then echo "Nix not installed. See docs/REPO_SETUP.md#nix-quickstart"; exit 1; fi
  nix --version
  nix flake show

nix-develop:
  if ! command -v nix >/dev/null 2>&1; then echo "Nix not installed. See docs/REPO_SETUP.md#nix-quickstart"; exit 1; fi
  echo "Entering Nix dev shell (exit with Ctrl-D)"
  nix develop -c $SHELL

nix-check:
  if ! command -v nix >/dev/null 2>&1; then echo "Nix not installed. See docs/REPO_SETUP.md#nix-quickstart"; exit 1; fi
  nix flake check
