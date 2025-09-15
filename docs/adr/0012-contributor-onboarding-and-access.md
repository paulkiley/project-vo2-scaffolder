# ADR 0012: Contributor Onboarding and Access

Date: 2025-09-15

## Status
Accepted

## Context
We need a clear, auditable process for adding/removing collaborators and granting the correct level of access, while keeping reviews fast and security tight.

## Decision
Use a team‑first, least‑privilege model with documented checklists.

### Roles and Permissions
- Owner/Admin: repository settings, branch protection, secrets; approves emergency overrides.
- Maintainer (Write): reviews/merges PRs, manages issues, triggers releases.
- Contributor (Write via PR): opens PRs from forks/branches; merges only via approvals.
- Triage (Triage): labels, issues, PR triage; no write to code.

Prefer GitHub Teams when available; refer to teams in CODEOWNERS (e.g., `@org/maintainers`). When teams are unavailable, list specific users.

### Onboarding (Checklist)
1) Identity & security
   - Require GitHub 2FA and (if org‑managed) SSO.
   - Confirm contributor’s GitHub handle and email.
2) Access level
   - Add to the appropriate team or directly to the repo with least privilege.
3) CODEOWNERS
   - Add the team (preferred) or user to relevant paths (scoped as narrowly as possible).
4) Branch protection & CI
   - Ensure required checks remain enforced; do not loosen protections for onboarding.
5) Docs & norms
   - Share CONTRIBUTING.md, SECURITY.md, GIT_GUIDE.md, and relevant ADRs (0007, 0008, 0011).
6) Tooling
   - Confirm local environment (Python, jq, just, nox) and access to the repo.

### Reviews and Approvals
- Early phase: approvals can be relaxed but CI checks remain required.
- Mature phase: require Code Owner review + at least 1 approval; squash merge enabled.
- Large changes: split into incremental PRs; use ADRs for rationale.

### Emergency Override
- Limited to Admins. Allowed for CI break/fix or security hotfix.
- Must:
  - Create a tracking issue referencing what was bypassed and why.
  - Follow up with a post‑incident PR/ADR within 48 hours.
  - Re‑enable normal protections immediately after.

### Offboarding (Checklist)
1) Remove from teams/repo and revoke any direct access.
2) Review open PRs/issues assigned; reassign as needed.
3) Rotate repo tokens/secrets if elevated access was held.
4) Update CODEOWNERS if entries referenced the user directly.

### Auditing
- Quarterly review of:
  - Repo collaborators and team membership vs CODEOWNERS.
  - Branch protection settings vs ADR 0008 & 0011.
  - Secrets and tokens (least privilege; rotate as needed).
- Use GitHub audit logs (org) or PR history for traceability.

## Consequences
- Pros: predictable, secure collaborator lifecycle; scoped ownership; fewer surprises.
- Cons: some overhead for reviews and periodic audits; team setup preferred.

## Alternatives Considered
- Ad‑hoc collaborator grants: fast but error‑prone; difficult to audit.
- Single‑owner model: simple but brittle and non‑scalable.
