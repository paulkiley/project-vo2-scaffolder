# ADR 0001: Manifest JSONL as Derived Artifact

Date: 2025-09-15

## Status

Accepted

## Context

We need a reliable way to reproduce the scaffolded project files across environments and over time. Keeping multi-line content in a shell heredoc leads to quoting and escaping issues, making it error-prone. We also need deterministic inputs for CI verification.

## Decision

Use a deterministically generated JSON Lines (JSONL) manifest (`file_contents.jsonl`) as the derived artifact, not the source of truth. The sources remain the committed files under `src/project_vo2_scaffolder/data_files` and adjacent code. The manifest encodes file content (base64), metadata (size, mode, sha256, mime), and path.

## Consequences

- Pros: deterministic, CI-verifiable, avoids quoting issues, supports binary content
- Cons: larger artifact size due to base64; an extra build step is required

## Alternatives Considered

- Heredocs: fragile escaping; hard to maintain
- Tarball checked into repo: opaque diffs; poor reviewability
