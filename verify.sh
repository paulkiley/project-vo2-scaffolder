#!/usr/bin/env bash
set -euo pipefail

info()    { echo -e "\033[34m[INFO]\033[0m $*"; }
success() { echo -e "\033[32m[SUCCESS]\033[0m $*"; }
error()   { echo -e "\033[31m[ERROR]\033[0m $*" >&2; exit 1; }

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE="$SCRIPT_DIR/file_contents.jsonl"
TMP=$(mktemp "$SCRIPT_DIR/file_contents.verify.XXXXXX.jsonl")

info "Rebuilding manifest to: $TMP"
bash "$SCRIPT_DIR/populate.sh" --out "$TMP"

info "Diffing $BASE against rebuilt manifest..."
if diff -u "$BASE" "$TMP"; then
  success "Manifest verified: no differences."
  rm -f "$TMP"
else
  error "Manifest differs from source files. See diff above. Keep temporary file: $TMP"
fi
