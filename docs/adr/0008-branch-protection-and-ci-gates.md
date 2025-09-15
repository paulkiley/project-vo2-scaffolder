# ADR 0008: Branch Protection and CI Gates

Date: 2025-09-15

## Status
Accepted

## Context
We want to prevent accidental pushes to `main` and ensure quality gates run.

## Decision
Protect `main` with:
- Require PRs for merge, at least 1 approving review.
- Require status checks to pass: `build-validate` (CI job).
- Enforce linear history (no merge commits), dismiss stale reviews, require up-to-date branches.
- Enforce for admins.

## Consequences
- Pros: consistent quality gates; predictable merges.
- Cons: occasional friction for hotfixes (use temporary exceptions if needed).
