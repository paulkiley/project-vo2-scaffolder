# ADR 0011: Quality Gates and CI Checks

Date: 2025-09-15

## Status
Accepted

## Context
We want consistent style, security scanning, and docs hygiene enforced in CI.

## Decision
- Python lint: Ruff for linting, Black for format checking.
- Security: Bandit (static analysis) and Gitleaks (secret scanning).
- Docs lint: markdownlint for Markdown, yamllint for YAML.
- All of the above must pass before rendering docs; these jobs are required checks.

## Consequences
- Pros: early detection of issues; consistent style; safer code.
- Cons: slightly longer CI runtime; occasional false positives.
