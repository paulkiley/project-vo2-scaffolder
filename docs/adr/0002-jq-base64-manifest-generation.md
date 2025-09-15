# ADR 0002: Generate Manifest with jq + base64

Date: 2025-09-15

## Status

Accepted

## Context

We must reliably convert the canonical repository files into a JSONL manifest that preserves bytes and metadata. Prior attempts with shell heredocs created invalid JSON due to escaping.

## Decision

Implement `populate.sh` to:

- Discover canonical files deterministically
- Compute `sha256`, `size_bytes`, `mode`, `executable`, and optional `mime_type`
- Base64-encode content with `base64` and assemble JSON per line using `jq`

## Consequences

- Pros: valid JSON always; robust across platforms; easy to diff and verify
- Cons: requires `jq` and `base64` in developer and CI environments

## Alternatives Considered

- Python-only builder: viable but increases coupling to Python runtime for a simple packaging task
- Tarball + manifest: heavier weight; less readable diffs

