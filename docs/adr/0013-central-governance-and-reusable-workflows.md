# ADR 0013: Central Governance and Reusable Workflows

Date: 2025-09-15

## Status
Accepted

## Context
Multiple repos need consistent GitOps practices (CI checks, security, docs hygiene, release automation). Copying files drifts; submodules add friction. We need a single source of truth that projects can consume by reference.

## Decision
Create a dedicated "governance" repository with:
- Reusable CI workflows (workflow_call) for lint, security scan, docs lint, and optional project-specific steps.
- Canonical templates (CODEOWNERS, issue/PR templates, CONTRIBUTING, SECURITY) delivered via Copier.
- ADR templates and central policy ADRs.
- A small updater (script/workflow) to bump workflow refs across repos when governance tags a new release.

Projects reference the reusable CI via:
```
uses: paulkiley/vo2-governance/.github/workflows/reusable-ci.yml@v1
```
They can override inputs or keep defaults, and retain repo-specific jobs if needed.

## Consequences
- Pros: single source of truth; easy to roll out changes via tag bumps; less drift.
- Cons: requires a central repo and release process; callers must update refs (automatable).

## Alternatives Considered
- Copying files: fastest initially, but drifts and multiplies fixes.
- Submodules/subtrees: higher maintenance, confusing for contributors.
- Org-level defaults: only available for organizations.
