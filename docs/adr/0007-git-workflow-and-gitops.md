# ADR 0007: Git Workflow and GitOps Practices

Date: 2025-09-15

## Status
Accepted

## Context
We need a simple, enforceable workflow that supports reviews, CI gates, and traceable changes.

## Decision
- Use trunk-based development on `main` with short-lived feature branches.
- All changes land via Pull Requests with at least 1 approval.
- Require passing CI (manifest validation + verify) before merge.
- Prefer squash merges to keep a clean, linear history.
- Use Conventional Commits for commit messages to aid changelogs and automation.

## Consequences
- Pros: simple, fast reviews, easy releases and rollbacks.
- Cons: requires discipline to keep branches short-lived and focused.

## Notes
- Long-form reasoning goes into ADRs and PR descriptions; commits remain atomic and concise.
