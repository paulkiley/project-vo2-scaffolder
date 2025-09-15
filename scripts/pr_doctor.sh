#!/usr/bin/env bash
set -euo pipefail

ok() { echo -e "\033[32m[OK]\033[0m $1"; }
warn() { echo -e "\033[33m[WARN]\033[0m $1"; }
err() { echo -e "\033[31m[ERROR]\033[0m $1"; }

status=0

check_file() {
  local p="$1"; local label="$2"
  if [[ -e "$p" ]]; then ok "$label present ($p)"; else err "$label missing ($p)"; status=1; fi
}

# Governance files
check_file ".github/CODEOWNERS" "CODEOWNERS"
check_file "CONTRIBUTING.md" "CONTRIBUTING"
check_file "SECURITY.md" "SECURITY"

# Python formatting/lint (optional if tools installed)
if command -v ruff >/dev/null 2>&1; then
  if ! ruff check .; then warn "Ruff found issues"; status=1; fi
else warn "Ruff not installed; skipping"; fi
if command -v black >/dev/null 2>&1; then
  if ! black --check .; then warn "Black formatting needed"; status=1; fi
else warn "Black not installed; skipping"; fi

# Markdown lint (optional)
if command -v markdownlint >/dev/null 2>&1; then
  if ! markdownlint **/*.md; then warn "Markdownlint issues"; status=1; fi
else warn "markdownlint not installed; skipping"; fi

# YAML lint (optional)
if command -v yamllint >/dev/null 2>&1; then
  if ! yamllint .; then warn "Yamllint issues"; status=1; fi
else warn "yamllint not installed; skipping"; fi

# Manifest sanity (if present)
if [[ -f noxfile.py && -f populate.sh ]]; then
  bash ./populate.sh || { err "populate.sh failed"; status=1; }
  if ! nox -s validate_manifest --error-on-missing-interpreters; then status=1; fi
fi

if [[ $status -eq 0 ]]; then ok "PR doctor checks passed"; else err "PR doctor found issues"; fi
exit $status
