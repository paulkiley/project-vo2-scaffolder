#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-_context}"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/context.txt"
{
  echo "# Repo Context"
  echo "PWD: $(pwd)"
  echo
  echo "## Git"
  (git rev-parse --abbrev-ref HEAD 2>/dev/null || true) | sed 's/^/branch: /'
  (git status -s 2>/dev/null || true)
  echo
  echo "## .work/backlog.yaml"
  [[ -f .work/backlog.yaml ]] && sed 's/^/  /' .work/backlog.yaml || echo "(missing)"
  echo
  echo "## .work/decisions.yaml"
  [[ -f .work/decisions.yaml ]] && sed 's/^/  /' .work/decisions.yaml || echo "(missing)"
  echo
  echo "## ADR files"
  rg -n "^# ADR" docs/adr 2>/dev/null || true
} > "$OUT_FILE"
echo "Wrote $OUT_FILE"
