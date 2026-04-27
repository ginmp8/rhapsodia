# Reporting Artifacts

Reporting artifacts communicate what was delivered after delivery activity. They must separate stakeholder-facing communication from internal-only detail and must preserve uncertainty when evidence is missing.

## feature-report.md

Purpose: Post-delivery report for one feature or spec. Store it in the selected spec package. It is useful to tech leads, stakeholders, operations, support, and future onboarding.

Required sections:

- `# Feature Report`
- `## Audience`
- `## Summary`
- `## Business Context`
- `## Delivered Scope`
- `## Impacted Systems`
- `## Changed Behavior`
- `## Evidence`
- `## Validation Evidence`
- `## Operational Impact`
- `## Rollout And Rollback`
- `## Risks And Limitations`
- `## Follow-ups`

Validation rules:

- Delivered scope must be based on delivery and execution evidence, not roadmap intent alone.
- Evidence and validation must be summarized; do not paste raw logs.
- Rollout and deployment status must cite evidence or be marked unknown, draft, pending, not released, or not recorded.
- Rollback notes must be present, even when rollback status is unknown.
- Follow-ups must be human-readable and must not become Mago-owned task decomposition.
- Internal-only details should move to `internal-notes.md`.

## release-notes.md

Purpose: Stakeholder-facing release communication for one or more delivered specs or features. Store it directly under `BOARD_ROOT`.

Required sections:

- `# Release Notes`
- `## Audience`
- `## Summary`
- `## User Impact`
- `## Changes`
- `## Availability And Rollout`
- `## Validation Status`
- `## Known Limitations`
- `## Support Notes`

Validation rules:

- Content must be stakeholder-facing and understandable without repository context.
- Do not claim availability, release, deployment, or production rollout without explicit evidence.
- If release evidence is missing, mark the artifact as draft or the rollout status as unknown, pending, not released, or not recorded.
- Do not expose internal-only language, private links, secrets, credentials, raw logs, branch names, commit hashes, or pull request status.
- Known limitations must be clear and non-sensitive.

## internal-notes.md

Purpose: Optional board-scoped companion notes for details that should not appear in `release-notes.md`. Store it directly under `BOARD_ROOT`.

Required sections when the file exists:

- `# Internal Notes`
- `## Summary`
- `## Internal Details`
- `## Follow-ups`

Validation rules:

- Keep internal-only content out of stakeholder-facing artifacts.
- Private references must not include secrets or credentials.
- Unknown facts must remain unknown.

Must not store:

- secrets, credentials, tokens, or raw sensitive operational data
- full raw execution logs
- branch, PR, commit, check, review, or deployment state as manually maintained source-of-truth fields
- delivery metadata that belongs in `ops.yaml`
