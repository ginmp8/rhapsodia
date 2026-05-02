# Reporting Artifacts

Reporting artifacts communicate delivered work after delivery activity, separate stakeholder-facing communication from internal-only detail, and preserve missing evidence as unknown.

## Evidence Provenance

Use Mago planning artifacts and Magia execution artifacts as read-only evidence. Attribute technical validation and implementation facts to their source, such as `according to validation-evidence.md`, `based on implementation-notes.md`, or `from supplied deployment evidence`. Magnomo may summarize the evidence for stakeholders, but it does not become the technical validator, deployer, reviewer, or acceptance authority.

## feature-report.md

Post-delivery report for one feature/spec in the selected spec package. Audience: tech leads, stakeholders, operations, support, future onboarding.

Required sections: `# Feature Report`, `## Audience`, `## Summary`, `## Business Context`, `## Delivered Scope`, `## Impacted Systems`, `## Changed Behavior`, `## Evidence`, `## Validation Evidence`, `## Operational Impact`, `## Rollout And Rollback`, `## Risks And Limitations`, `## Follow-ups`.

Rules: delivered scope comes from delivery/execution evidence, not roadmap intent alone; summarize evidence/validation with source attribution and do not paste raw logs; technical validation status must come from Magia evidence or supplied check/deployment records, never from Magnomo assertion; rollout/deployment status cites evidence or is `unknown`, `draft`, `pending`, `not released`, or `not recorded`; rollback notes exist even when unknown; follow-ups stay human-readable and not Mago task decomposition; move internal-only detail to `internal-notes.md`.

## release-notes.md

Stakeholder-facing release communication for delivered specs/features directly under `BOARD_ROOT`.

Required sections: `# Release Notes`, `## Audience`, `## Summary`, `## User Impact`, `## Changes`, `## Availability And Rollout`, `## Validation Status`, `## Known Limitations`, `## Support Notes`.

Rules: content is understandable without repository context; do not claim availability, release, deployment, technical validation, or production rollout without explicit evidence; missing release or validation evidence means draft/status `unknown`, `pending`, `not released`, or `not recorded`; do not expose internal-only language, private links, secrets, credentials, raw logs, branch names, commit hashes, or PR status; known limitations are clear and non-sensitive.

## internal-notes.md

Optional board-scoped companion for details excluded from `release-notes.md`, directly under `BOARD_ROOT`.

Required sections when present: `# Internal Notes`, `## Summary`, `## Internal Details`, `## Follow-ups`.

Rules: keep internal-only content out of stakeholder artifacts; private references must not include secrets or credentials; unknown facts remain unknown.

Must not store secrets, credentials, tokens, raw sensitive operational data, full raw execution logs, branch/PR/commit/check/review/deployment state as manually maintained source of truth, or delivery metadata that belongs in `ops.yaml`.
