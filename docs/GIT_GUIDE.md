# Git and PR Guide

## Commit Messages (Conventional Commits)
- feat(scope): add new capability
- fix(scope): correct a bug
- docs(scope): documentation changes
- chore(scope): tooling, CI, build
- refactor(scope): no functional change
- test(scope): tests

Include a short imperative subject, followed by an optional body explaining why.

## Atomic Commits
- Each commit should encapsulate one logical change.
- Avoid mixing unrelated changes; follow-up commits are fine.

## Pull Requests
- Keep PRs small and focused; reference issues/ADRs.
- Provide context: what changed, why, alternatives considered.
- Checklists:
  - [ ] CI green
  - [ ] Docs/ADRs updated if needed
  - [ ] No secrets in diffs

## Long-form Descriptions
- Use PR descriptions and ADRs for deeper context.
- Summarize in CHANGELOG at release time.

## Merges
- Prefer squash merge for linear history.
- Rebase your branch before merge if out of date.
