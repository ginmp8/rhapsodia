# Delivery Artifacts

Delivery artifacts belong to Magnomo. They communicate human delivery governance without becoming implementation plans or execution records.

Repository-facing `ops.yaml`, `status.md`, `stakeholder-brief.md`, and `replanning.md` belong in one selected spec package under `BOARD_ROOT/specs/<spec_id>/`.

Repository-facing `portfolio.yaml` and `portfolio.md` stay directly under `BOARD_ROOT`.

## ops.yaml

Structured source of truth for delivery metadata.

Required top-level keys:

- `schema_version`
- `spec_id`
- `request`
- `ownership`
- `planning`
- `priority`
- `status`
- `blockers`
- `replanning`
- `tags`
- `links`

Required nested keys must exist, but values may be `null`, `unknown`, or empty lists when facts are missing:

- `request.title`
- `request.requester`
- `request.requested_date`
- `request.source`
- `ownership.owner`
- `ownership.backup_owner`
- `ownership.stakeholders`
- `planning.sprint`
- `planning.bucket`
- `planning.target_date`
- `planning.commitment`
- `priority.level`
- `priority.rationale`
- `status.state`
- `status.summary`
- `status.updated_at`
- `links.mago`
- `links.magia`
- `links.external`

Optional delivery fields should be present in new files when practical. Missing optional fields warn, not fail:

- `request.context`
- `ownership.decision_maker`
- `ownership.watchers`
- `planning.milestone`
- `planning.rollout_target`
- `priority.urgency`
- `priority.impact`
- `priority.risk`
- `priority.cost_of_delay`
- `status.confidence`
- `status.evidence_summary`
- `status.manual`
- `status.inferred`
- `risks`
- `repos.candidate_impacted`

Enums:

- `request.source`: `unknown`, `github_issue`, `chat`, `email`, `rough_demand`, `roadmap`, `support_ticket`, `customer_request`, `incident`, `manual`, `other`
- `planning.bucket`: `unknown`, `customer_commitment`, `revenue`, `retention`, `growth`, `risk_reduction`, `compliance`, `platform`, `maintenance`, `support`, `incident`, `roadmap`, `quality`, `research`, `other`
- `planning.commitment`: `unknown`, `committed`, `targeted`, `tentative`
- `priority.level`: `unknown`, `low`, `medium`, `high`, `urgent`
- `priority.urgency`: `unknown`, `low`, `medium`, `high`, `immediate`
- `priority.impact`: `unknown`, `low`, `medium`, `high`, `critical`
- `priority.risk`: `unknown`, `low`, `medium`, `high`, `critical`
- `status.state`: `unknown`, `intake`, `triage`, `planned`, `in_progress`, `blocked`, `at_risk`, `done`, `canceled`
- `status.confidence`: `unknown`, `low`, `medium`, `high`

Rules:

- `schema_version` must be `1`.
- Repository-facing `spec_id` must match `specNNN` and the enclosing selected spec package.
- Off-repository intake drafts may keep `spec_id` as `null` until a spec is assigned.
- Dates must use `YYYY-MM-DD`.
- `ownership.stakeholders`, `ownership.watchers`, `blockers`, `risks`, `replanning`, `tags`, `repos.candidate_impacted`, and every `links.*` value must be lists.
- Missing owner, stakeholders, target date, priority, urgency, impact, risk, and candidate impacted repos warn, not fail.
- Invalid enum values, malformed dates, broken types, missing required keys, and malformed replanning entries fail.
- A replanning entry that changes `target_date`, `sprint`, `scope`, `owner`, or `commitment` must include `date`, `changed_fields`, `from`, `to`, `reason`, and `impact`.

Expected collection shapes:

- `ownership.stakeholders`, `ownership.watchers`, `status.inferred.evidence`, `tags`, `repos.candidate_impacted`, and every `links.*` entry are non-empty strings.
- `blockers[]` entries are mappings with `id`, `summary`, optional `owner`, and optional `needed_by`.
- `risks[]` entries are mappings with `id`, `summary`, `severity`, and optional `owner`.
- `replanning[]` entries are mappings with `date`, `changed_fields`, `reason`, `impact`, and conditional `from` and `to` fields for material field changes.

Authoring rule:

- Use `scripts/write_ops_scaffold.py <path> --spec-id <specNNN>` or `scripts/write_artifact_scaffold.py <path> --spec-id <specNNN>` to create new `ops.yaml` files. Do not freehand a fresh `ops.yaml` shape.
- Use `scripts/update_template_lists.py <path> --data <payload.yaml>` to populate `ownership.stakeholders`, `ownership.watchers`, `status.inferred.evidence`, `blockers`, `risks`, `replanning`, `tags`, `repos.candidate_impacted`, and `links.*`; check supported shapes with `scripts/update_template_lists.py --schema --artifact-name ops.yaml`.
- After writing or editing `ops.yaml`, run `scripts/validate_artifact.py <path>` or `scripts/validate_ops.py <path>` before treating it as valid.

Must not store:

- Branches, pull requests, commits, checks, reviews, deployment state, or last commit age as maintained fields.
- Raw execution logs or test output.
- Mago task decomposition or implementation-ready plans.
- Internal-only stakeholder politics or sensitive private details.

## status.md

Human-readable status derived from `ops.yaml` and optional supplied evidence.

Store `status.md` beside `ops.yaml` in the selected spec package.

Required sections:

- `# Status`
- `## Summary`
- `## Current State`
- `## Manual Status`
- `## Inferred Status`
- `## Risks And Blockers`
- `## Next Steps`
- `## Unknowns`

Optional sections:

- `## Evidence`
- `## Recent Changes`
- `## Decisions Needed`
- `## Stakeholders`

Rules:

- Manual status must come from explicit human-entered status in `ops.yaml` or notes.
- Inferred status must cite supplied or linked planning/execution evidence.
- Unknown status, validation, release, or deployment evidence must remain unknown.
- Risks and blockers must align with structured `ops.yaml` blockers and risks when present.

Must not store manually maintained branch, pull request, commit, check, review, or deployment state.

## stakeholder-brief.md

Business-facing delivery summary for stakeholders.

Store `stakeholder-brief.md` beside `ops.yaml` in the selected spec package.

Required sections:

- `# Stakeholder Brief`
- `## Summary`
- `## Decision Needed`
- `## Impact`
- `## Timing`
- `## Risks`

Optional sections:

- `## Audience`
- `## Non-Goals`
- `## Dependencies`
- `## Communication Plan`

Rules:

- Create when stakeholder communication, timing alignment, decision making, or risk communication is required.
- Timing, ownership, and risk must match `ops.yaml` or be marked unknown.
- Keep implementation details out unless needed to explain impact or risk.
- Move internal-only details to `internal-notes.md` only if reporting work is explicitly in scope.

## replanning.md

Append-only narrative history for material delivery changes.

Store `replanning.md` beside `ops.yaml` in the selected spec package.

Required sections:

- `# Replanning`
- `## Entries`

Rules:

- Append new entries using `### YYYY-MM-DD - <summary>`.
- Include changed fields, from, to, reason, impact, and decision maker when known.
- Mirror structured changes in `ops.yaml.replanning`.
- Do not rewrite old entries except with a dated correction.
- Do not use replanning for routine status updates.

## portfolio.yaml

Machine-readable consolidated delivery portfolio.

Store `portfolio.yaml` directly under `BOARD_ROOT`.

Required top-level keys:

- `schema_version`
- `portfolio_id`
- `updated_at`
- `items`
- `blocked`
- `risks`
- `replans`

Recommended top-level keys:

- `flags.blocked`
- `flags.overdue`
- `flags.replanned`
- `flags.missing_owner`
- `flags.at_risk`
- `flags.multi_repo`

Item fields:

- `spec_id`
- `feature_key`
- `title`
- `owner`
- `state`
- `target_date`
- `priority`
- `urgency`
- `impact`
- `risk`
- `confidence`
- `candidate_impacted_repos`
- `source`

Rules:

- `schema_version` must be `1`.
- `updated_at` and item `target_date` values must use `YYYY-MM-DD`.
- Item `spec_id` must be `null` or match `specNNN`.
- Item `state`, `priority`, `urgency`, `impact`, `risk`, and `confidence` use the same enums as `ops.yaml`.
- `items`, `blocked`, `risks`, `replans`, `flags.*`, and `candidate_impacted_repos` must be lists where present.
- Populate `items`, `blocked`, `risks`, `replans`, and `flags.*` with `scripts/update_template_lists.py <portfolio.yaml> --data <payload.yaml>`; do not hand-shape portfolio list entries.
- Missing item owner warns.
- Duplicate spec IDs warn.
- Past target dates on non-terminal items warn as overdue.
- Items with more than one candidate impacted repo should appear in `flags.multi_repo`.

## portfolio.md

Human-readable consolidated delivery portfolio.

Store `portfolio.md` directly under `BOARD_ROOT`.

Required sections:

- `# Portfolio`
- `## Summary`
- `## Items`
- `## Blocked`
- `## Overdue`
- `## Missing Owners`
- `## At Risk`
- `## Multi-Repo`
- `## Risks`
- `## Replans`

Rules:

- Derive the summary from `portfolio.yaml`, `ops.yaml`, and available evidence.
- Do not introduce new canonical delivery metadata that belongs in `ops.yaml` or `portfolio.yaml`.
- Unknown placeholders warn until intentionally retained.
