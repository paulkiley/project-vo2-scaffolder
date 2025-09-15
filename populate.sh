#!/usr/bin/env bash

# @project: Project VO2 Bootstrapper
# @file:    populate.sh
# @brief:   Builds file_contents.jsonl from the canonical files in this repo.

set -euo pipefail

# --- Colored output helpers ---
info()    { echo -e "\033[34m[INFO]\033[0m $*"; }
success() { echo -e "\033[32m[SUCCESS]\033[0m $*"; }
error()   { echo -e "\033[31m[ERROR]\033[0m $*" >&2; exit 1; }

# --- Pre-flight checks ---
command -v jq >/dev/null 2>&1 || error "jq is required. Please install jq."
command -v base64 >/dev/null 2>&1 || error "base64 is required."

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
OUT_DEFAULT="$SCRIPT_DIR/file_contents.jsonl"
OUT="$OUT_DEFAULT"

# --- Args ---
while [[ ${1:-} ]]; do
  case "$1" in
    --out)
      OUT="${2:?--out requires a path}"
      shift 2
      ;;
    -h|--help)
      cat <<USAGE
Usage: $(basename "$0") [--out path]
  --out path   Write JSONL to the given path (default: $OUT_DEFAULT)
USAGE
      exit 0
      ;;
    *)
      error "Unknown argument: $1"
      ;;
  esac
done

# --- Collect canonical source files ---
# We encode files from the existing repo so content is the single source of truth.
mapfile -t DATA_FILES < <(
  {
    printf '%s\n' \
      "$ROOT_DIR/pyproject.toml" \
      "$ROOT_DIR/src/project_vo2_scaffolder/__main__.py";
    find "$ROOT_DIR/src/project_vo2_scaffolder/data_files" -type f | sort;
  } | awk 'NF' | sort -u
)

if [[ ${#DATA_FILES[@]} -eq 0 ]]; then
  error "No source files found to populate JSONL."
fi

info "Building JSONL database from ${#DATA_FILES[@]} files..."
: > "$OUT"

sha256_calc() {
  local f="$1"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$f" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$f" | awk '{print $1}'
  else
    error "Missing shasum/sha256sum for checksum"
  fi
}

file_mode_octal() {
  local f="$1"
  if stat -f %p "$f" >/dev/null 2>&1; then
    # macOS: includes file type bits (e.g., 100644) -> take last 4
    local p
    p=$(stat -f %p "$f")
    echo "${p: -4}"
  else
    # Linux: just the permission bits
    local p
    p=$(stat -c %a "$f")
    if [[ ${#p} -eq 3 ]]; then echo "0$p"; else echo "$p"; fi
  fi
}

mime_type_of() {
  local f="$1"
  if command -v file >/dev/null 2>&1; then
    file -b --mime-type "$f" 2>/dev/null || echo ""
  else
    echo ""
  fi
}

for abs in "${DATA_FILES[@]}"; do
  if [[ ! -f "$abs" ]]; then
    error "Missing source file: $abs"
  fi
  rel="${abs#${ROOT_DIR}/}"
  # Base64 encode without newlines for clean JSONL.
  b64=$(base64 < "$abs" | tr -d '\n')
  size=$(wc -c < "$abs" | tr -d ' ')
  sha=$(sha256_calc "$abs")
  mode=$(file_mode_octal "$abs")
  mime=$(mime_type_of "$abs")
  # Compute executable flag from mode bits
  perm=$(( 8#$mode ))
  if (( perm & 73 )); then exec=true; else exec=false; fi
  jq -nc \
    --arg path "$rel" \
    --arg content "$b64" \
    --arg sha "$sha" \
    --arg mode "$mode" \
    --arg mime "$mime" \
    --argjson size "$size" \
    --argjson exec "$exec" \
    '{schema_version:1, path:$path, encoding:"base64", content:$content, sha256:$sha, size_bytes:$size, mode:$mode, executable:$exec} | if $mime != "" then . + {mime_type:$mime} else . end' \
    >> "$OUT"
done

success "Created $OUT"

# --- Manifest meta ---
META_OUT="$SCRIPT_DIR/manifest_meta.json"
info "Writing manifest metadata: $META_OUT"

# Extract tool version from pyproject.toml
TOOL_VERSION=$(awk -F '"' '/^version\s*=/{print $2; exit}' "$ROOT_DIR/pyproject.toml" 2>/dev/null || true)
TOOL_VERSION=${TOOL_VERSION:-unknown}

SCHEMA_VERSION=1
ENTRIES=$(wc -l < "$OUT" | tr -d ' ')
COMMIT="${SOURCE_COMMIT:-}"
if [[ -z "$COMMIT" ]] && command -v git >/dev/null 2>&1; then
  COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || true)
fi
COMMIT=${COMMIT:-unknown}

JQ_VER=$(jq --version 2>/dev/null || echo "jq unknown")
BASE64_VER=$(base64 --version 2>/dev/null | head -n1 || echo "base64 unknown")
OS_INFO=$(uname -srm 2>/dev/null || echo "unknown")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

jq -nc \
  --arg schema_version "$SCHEMA_VERSION" \
  --arg tool_version "$TOOL_VERSION" \
  --arg source_commit "$COMMIT" \
  --arg generated_at "$NOW" \
  --arg jq_version "$JQ_VER" \
  --arg base64_version "$BASE64_VER" \
  --arg os "$OS_INFO" \
  --argjson entries "$ENTRIES" \
  '{schema_version: ($schema_version|tonumber), tool_version: $tool_version, source_commit: $source_commit, generated_at: $generated_at, entries: $entries, generator: {script: "populate.sh", jq: $jq_version, base64: $base64_version, os: $os}}' \
  > "$META_OUT"

success "Wrote $META_OUT"
