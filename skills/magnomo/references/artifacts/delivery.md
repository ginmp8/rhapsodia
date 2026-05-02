# Delivery Artifacts

Magnomo delivery artifacts communicate human delivery governance, not implementation plans or execution records.

Placement: spec-scoped `ops.yaml`, `status.md`, `stakeholder-brief.md`, `replanning.md` live under `BOARD_ROOT/specs/<spec_id>/`. Board-scoped `portfolio.yaml` and `portfolio.md` live directly under `BOARD_ROOT`.

## ops.yaml

Structured source of truth for one spec's delivery metadata.

Required top-level keys: `schema_version`, `spec_id`, `request`, `ownership`, `planning`, `priority`, `status`, `blockers`, `replanning`, `tags`, `links`.

Required nested keys: `request.title`, `request.requester`, `request.requested_date`, `request.source`, `ownership.owner`, `ownership.backup_owner`, `ownership.stakeholders`, `planning.sprint`, `planning.bucket`, `planning.target_date`, `planning.commitment`, `priority.level`, `priority.rationale`, `status.state`, `status.summary`, `status.updated_at`, `links.mago`, `links.magia`, `links.external`. Values may be `null`, `unknown`, or empty lists when facts are missing.

Optional fields for new files when practical: `request.context`, `ownership.decision_maker`, `ownership.watchers`, `planning.milestone`, `planning.rollout_target`, `priority.urgency`, `priority.impact`, `priority.risk`, `priority.cost_of_delay`, `status.confidence`, `status.evidence_summary`, `status.manual`, `status.inferred`, `risks`, `repos.candidate_impacted`. Missing optional fields warn, not fail.

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

Rules: `schema_version` = `1`; repository `spec_id` matches `specNNN` and enclosing spec package; off-repository drafts may keep `spec_id: null`; dates use `YYYY-MM-DD`; `ownership.stakeholders`, `ownership.watchers`, `blockers`, `risks`, `replanning`, `tags`, `repos.candidate_impacted`, and all `links.*` values are lists. Missing owner, stakeholders, target date, priority, urgency, impact, risk, and candidate repos warn. Invalid enums, dates, types, required keys, or replanning entries fail. Replanning changes to `target_date`, `sprint`, `scope`, `owner`, or `commitment` require `date`, `changed_fields`, `from`, `to`, `reason`, `impact`.

Collection shapes: simple-list entries (`ownership.stakeholders`, `ownership.watchers`, `status.inferred.evidence`, `tags`, `repos.candidate_impacted`, `links.*`) are non-empty strings. `blockers[]`: mappings with `id`, `summary`, optional `owner`, `needed_by`. `risks[]`: mappings with `id`, `summary`, `severity`, optional `owner`. `replanning[]`: mappings with `date`, `changed_fields`, `reason`, `impact`, plus conditional `from`/`to` for material changes.

Authoring: create with `scripts/write_ops_scaffold.py <path> --spec-id <specNNN>` or `scripts/write_artifact_scaffold.py <path> --spec-id <specNNN>`; never freehand a fresh shape. Populate supported lists with `scripts/update_template_lists.py <path> --data <payload.yaml>`; inspect support via `scripts/update_template_lists.py --schema --artifact-name ops.yaml`. Validate with `scripts/validate_artifact.py <path>` or `scripts/validate_ops.py <path>`.

Must not store branches, PRs, commits, checks, reviews, deployment state, last commit age, raw logs, test output, Mago task decomposition, implementation-ready plans, internal-only politics, or sensitive private details.

## status.md

Human status beside `ops.yaml`, derived from `ops.yaml` and supplied evidence.

Required sections: `# Status`, `## Summary`, `## Current State`, `## Manual Status`, `## Inferred Status`, `## Risks And Blockers`, `## Next Steps`, `## Unknowns`. Optional: `## Evidence`, `## Recent Changes`, `## Decisions Needed`, `## Stakeholders`.

Rules: manual status comes from explicit human-entered status in `ops.yaml` or notes; inferred status cites supplied/linked planning or execution evidence; unknown status, validation, release, or deployment remains unknown; risks/blockers align with structured `ops.yaml` when present. Do not maintain branch, PR, commit, check, review, or deployment state.

## stakeholder-brief.md

Business-facing summary beside `ops.yaml` for stakeholder communication, timing alignment, decisions, or risk communication.

Required sections: `# Stakeholder Brief`, `## Summary`, `## Decision Needed`, `## Impact`, `## Timing`, `## Risks`. Optional: `## Audience`, `## Non-Goals`, `## Dependencies`, `## Communication Plan`.

Rules: timing, ownership, and risk match `ops.yaml` or stay unknown; keep implementation detail out unless needed for impact/risk; move internal-only details to `internal-notes.md` only when reporting work is in scope.

## replanning.md

Append-only material delivery-change history beside `ops.yaml`.

Required sections: `# Replanning`, `## Entries`. Append entries as `### YYYY-MM-DD - <summary>` with changed fields, from, to, reason, impact, and decision maker when known. Mirror structured changes in `ops.yaml.replanning`. Do not rewrite old entries except via dated correction. Do not use for routine status updates.

## portfolio.yaml

Machine-readable board portfolio under `BOARD_ROOT`.

Required top-level keys: `schema_version`, `portfolio_id`, `updated_at`, `items`, `blocked`, `risks`, `replans`. Recommended keys: `flags.blocked`, `flags.overdue`, `flags.replanned`, `flags.missing_owner`, `flags.at_risk`, `flags.multi_repo`.

Item fields: `spec_id`, `feature_key`, `title`, `owner`, `state`, `target_date`, `priority`, `urgency`, `impact`, `risk`, `confidence`, `candidate_impacted_repos`, `source`.

Rules: `schema_version` = `1`; `updated_at` and `target_date` use `YYYY-MM-DD`; item `spec_id` is `null` or `specNNN`; item `state`, `priority`, `urgency`, `impact`, `risk`, `confidence` reuse `ops.yaml` enums; `items`, `blocked`, `risks`, `replans`, `flags.*`, `candidate_impacted_repos` are lists. Populate lists with `scripts/update_template_lists.py <portfolio.yaml> --data <payload.yaml>`; do not hand-shape entries. Missing item owner, duplicate spec IDs, overdue non-terminal items, and multi-repo items warn.

## portfolio.md

Human board portfolio under `BOARD_ROOT`.

Required sections: `# Portfolio`, `## Summary`, `## Items`, `## Blocked`, `## Overdue`, `## Missing Owners`, `## At Risk`, `## Multi-Repo`, `## Risks`, `## Replans`.

Rules: derive summary from `portfolio.yaml`, `ops.yaml`, and evidence; do not introduce canonical metadata that belongs in `ops.yaml` or `portfolio.yaml`; unknown placeholders warn until intentionally retained.
