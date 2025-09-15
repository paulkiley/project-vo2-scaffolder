# ADR 0006: Versioning and Distribution Strategy

Date: 2025-09-15

## Status

Accepted

## Context

The scaffolder produces a JSONL manifest and renders documentation/templates. We need a clear strategy to version schemas and ship artifacts so other environments (CI, fresh machines, or users) can reliably consume them.

## Decision

1) Versioning

- Use Semantic Versioning (SemVer) for the scaffolder package and CLI.
- Use a manifest-level `schema_version` as the canonical schema version; per-entry `schema_version` is optional for forward/backward compatibility.
- Version-bump policy:
  - Patch: content or template changes that do not alter schema.
  - Minor: additive schema changes (new optional fields; backward compatible).
  - Major: breaking schema changes (field removals/renames; semantics change).

2) Distribution

- Primary: GitHub Releases on tags (`vX.Y.Z`), with:
  - `file_contents.jsonl` (manifest)
  - `manifest_meta.json` (provenance: schema, tool version, commit, generator versions, entry count, timestamp)
  - `data_files.zip` (zip of `src/project_vo2_scaffolder/data_files`)
  - `CHECKSUMS.txt` (SHA256 for the above files)
  - Optional: `rendered-docs-default.zip` (Jinja2 templates rendered with defaults)
- Secondary: Publish Python package to PyPI for convenient CLI install (`pipx install project-vo2-scaffolder`).

3) Provenance

- The release includes `manifest_meta.json` with: `schema_version`, `tool_version`, `source_commit`, `generated_at`, generator versions, and `entries`.

## Consequences

- Pros: predictable consumption; reproducible releases; easy offline usage.
- Cons: small overhead to produce and store release assets.

## Alternatives Considered

- Publish only the package: good for Python users but less friendly for shell-only consumers.
- Single tarball of everything: acceptable but less reviewable; separate assets improve clarity.
- OCI-only distribution: powerful, but unnecessary complexity for this use case today.
