# ADR 0003: Task Runner and Validation

Date: 2025-09-15

## Status

Accepted

## Context

We need ergonomic local workflows and CI-friendly validation.

## Decision

- Use `just` as the local task runner (DX-first, simple syntax)
- Provide `nox` session `validate_manifest` for pure-stdlib checks (JSON/base64/sha256/mode)
- Add `verify.sh` to rebuild and diff the manifest against sources

## Consequences

- Pros: easy local usage; CI parity; language-agnostic validation
- Cons: developers must install small toolset (`just`, `nox`, `jq`)

## Alternatives Considered

- Make: works, but ergonomics and cross-platform quirks are less ideal
- Bazel/Pants: heavy for this repo’s scope
