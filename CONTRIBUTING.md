# Contributing Guide

Thank you for your interest in contributing! This project uses a simple, review-friendly workflow.

## Workflow
- Trunk-based on `main` with short-lived feature branches.
- All changes go through Pull Requests (PRs) with CI checks.
- Prefer squash merge for a linear history.

## Commit Messages (Conventional Commits)
- feat(scope): add new capability
- fix(scope): correct a bug
- docs(scope): documentation changes
- chore(scope): tooling, CI, build
- refactor(scope): no functional change
- test(scope): tests

Keep subjects short and imperative. Use body text for “why” when helpful.

## PR Checklist
- [ ] CI green (lint, security, docs, validate)
- [ ] ADRs/docs updated if needed
- [ ] No secrets or credentials committed
- [ ] Conventional commit(s)

## Local Development
- Tasks: `just` shows available commands
- Build manifest: `just db`, validate: `just validate`, verify: `just verify`
- Lint locally (optional): `ruff check .` and `black --check .`

## Reporting Issues
- Use issue templates for bugs and feature requests. Include steps to reproduce and context.

## Code of Conduct
- Be respectful and constructive. Assume good intent. Help others succeed.
