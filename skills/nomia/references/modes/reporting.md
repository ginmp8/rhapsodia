# Reporting Mode

Use for `feature-report` and `release-notes`.

## Canonical Rules

`BOARD_ROOT` is required for repository-facing reporting. Prompt `BOARD_ROOT` wins after validation; otherwise derive it from `references/canonical-paths.md`. `feature-report` requires a selected spec package under `BOARD_ROOT/specs/<spec_id>/`; `feature-report.md` stays there. `release-notes.md` and `internal-notes.md` stay directly under `BOARD_ROOT`.

Create/refresh reports with local scripts whenever available: scaffold with `scripts/write_artifact_scaffold.py`; validate with `scripts/validate_artifact.py` instead of copying template text.

Reporting starts after delivery activity has evidence. It turns nomia metadata and supplied delivery evidence into human-ready communication without inventing facts.

Reporting consumes Magia execution evidence and Mago planning evidence as source material. Attribute technical statements to their source and keep nomia authority limited to delivery communication, governance status, and stakeholder-readable summaries.

## feature-report

Create `feature-report.md` for one delivered feature/spec. Audience: tech leads, stakeholders, operations, support, future onboarding. Include business context, delivered scope, explicit non-scope, impacted systems, changed behavior, evidence, validation summary, operational impact, rollout/rollback notes, risks, limitations, follow-ups. Do not turn follow-ups into Mago task decomposition.

## release-notes

Create board-scoped `release-notes.md` for delivered specs/features. Audience: stakeholders, users, support, customer-facing teams, and readers without repository context. Include user impact, visible changes, availability/rollout status, known limitations, and support notes. Put implementation details, unresolved internal risks, private links, operational watchpoints, or private support context in `internal-notes.md`.

## Evidence Rules

Do not claim shipment without explicit release, deployment, or rollout evidence. Do not claim technical validation, production readiness, or test completion unless the supplied evidence says so; phrase it as sourced evidence, not nomia validation. Mark missing release, rollout, or validation evidence as unknown/draft/pending/not recorded. Do not expose internal-only details in `release-notes.md`; place them in `internal-notes.md`. Never include secrets, credentials, private tokens, or raw sensitive operational data. `internal-notes.md` requires the Privacy Handling metadata and remains non-shareable externally by default.
