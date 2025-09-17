# ADR 0005: Integrity, Path Safety, and Permissions

Date: 2025-09-15

## Status

Accepted

## Context

Materializing files from a manifest must be safe (no path traversal), correct (byte-accurate), and respect executable bits.

## Decision

- Include `sha256`, `size_bytes`, and `mode` in manifest entries
- Enforce path safety in `02-populate-files.py` (no absolute paths or `..` components; ensure within CWD)
- Apply `mode` if present; otherwise set executable bit for `.sh` and shebang files

## Consequences

- Pros: early failure on tampering or mismatches; consistent permissions across hosts
- Cons: slightly more complexity and metadata in the manifest

## Alternatives Considered

- Trust content implicitly: less safe; hard to audit
