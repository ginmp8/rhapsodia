# Reporting Mode

## Canonical Rules

- `BOARD_ROOT` is required for repository-facing reporting artifacts.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; otherwise derive it from `references/canonical-paths.md`.
- `feature-report` requires a selected spec package under `BOARD_ROOT/specs/<spec_id>/`.
- Keep `feature-report.md` in the selected spec package.
- Keep `release-notes.md` and `internal-notes.md` directly under `BOARD_ROOT`.
- Create or refresh reporting artifacts with local scripts whenever a script can perform the template-backed operation. Use `scripts/write_artifact_scaffold.py` for scaffold writes and validate with `scripts/validate_artifact.py` instead of copying or checking template text manually.

Use for `feature-report` and `release-notes`.

Reporting starts after delivery activity has evidence. It turns Magnomo delivery metadata and supplied delivery evidence into human-ready communication without inventing facts.

## feature-report

Create `feature-report.md` in the selected spec package for one delivered feature or spec.

Audience: tech leads, stakeholders, operations, support, and future onboarding.

Include:

Business context, delivered scope, explicit non-scope, impacted systems, changed behavior, evidence, validation summary, operational impact, rollout/rollback notes, risks, limitations, and follow-ups.

Do not turn follow-ups into Mago implementation task decomposition.

## release-notes

Create board-scoped `release-notes.md` for one or more delivered specs or features.

Audience: stakeholders, users, support, customer-facing teams, and readers who should not need repository or implementation context.

Include user impact, visible changes, availability or rollout status, known limitations, and support notes. Keep the language stakeholder-facing. Use `internal-notes.md` for implementation details, unresolved internal risks, private links, operational watchpoints, or private support context that should not appear in stakeholder-facing communication.

## Evidence Rules

- Do not claim a feature shipped without explicit release, deployment, or rollout evidence.
- Mark missing release, rollout, or validation evidence as unknown, draft, pending, or not recorded.
- Do not expose internal-only details in `release-notes.md`.
- Put sensitive or internal-only delivery details in `internal-notes.md`.
- Never include secrets, credentials, private tokens, or raw sensitive operational data.
