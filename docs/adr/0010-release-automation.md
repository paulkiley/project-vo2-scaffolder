# ADR 0010: Automated Versioning and Changelog

Date: 2025-09-15

## Status
Accepted

## Context
Manual tagging and changelog maintenance are error-prone. The repo uses Conventional Commits.

## Decision
Adopt Release Please to create release PRs and tags based on Conventional Commits. Keep the existing release workflow for packaging artifacts; it triggers on tags created by Release Please.

## Consequences
- Pros: automated releases, consistent changelogs.
- Cons: requires disciplined commit messages.
