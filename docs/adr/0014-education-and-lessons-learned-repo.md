# ADR 0014: Education and Lessons Learned Repository

Date: 2025-09-15

## Status
Accepted

## Context
We want a durable, practical learning path for contributors that goes beyond abstract best practices: real incidents, root-cause analysis, failed experiments, and how policies evolved. Mixing training artifacts with product repos clutters history and makes curation hard.

## Decision
Create a dedicated public repo (e.g., `vo2-academy`) for:
- Modular learning tracks (GitOps, CI/CD, security, docs, releases) with outcomes and exercises.
- Case studies from our own PRs/issues/incidents (sanitized), each with:
  - Problem statement, context
  - RCA (5-whys), what we tried, what worked/didn’t
  - Policy/ADR changes that resulted
  - Practice tasks to reinforce learning
- “Update loop” process: when a project RCA closes, open a PR in the academy to add/update the related module.

## Consequences
- Pros: onboards contributors faster; institutional memory; demonstrates why policies exist; improves consistency.
- Cons: ongoing curation work; must scrub sensitive data before publishing.

## Implementation Notes
- Start small: GitOps + CI failures we fixed here (manifest generation, lint/security gates, branch protection strategy).
- Structure modules as Markdown with checklists and links to live PRs.
- Add a Copier template so new modules have a consistent format.
- Encourage PRs from contributors who complete modules to add reflections.
