# Validation

Use for `validate-contracts` and `normalize-human-artifacts`.

## Canonical Rules

`BOARD_ROOT` is required when validation touches repository-facing nomia artifacts. Prompt `BOARD_ROOT` wins after validation; otherwise derive it from `references/canonical-paths.md`. A selected spec path is required only for spec-scoped validation. Keep scope to nomia artifacts and boundaries under `BOARD_ROOT` and selected spec packages.

nomia validators check artifacts and ownership boundaries. They do not execute repository code, load Mago/Magia skill files, or infer missing facts.

## Skill Root Convention

Use `<skill-root>` for the root folder of this skill package. In this repository that is usually `skills/nomia`; when installed under GitHub/Copilot conventions it may be `.github/skills/nomia`; when extracted from a package it may be `nomia`.

## Scripts

- `scripts/guide_intake.py`: inspect partial YAML/JSON intake evidence and emit non-authoritative profile, lifecycle, blocker, unknown, and next-step guidance.
- `scripts/evaluate_governance.py`: evaluate transitions, metrics, and typed handoffs; handoff results include missing-field and remediation diagnostics without changing contract authority.
- `scripts/project_governance_views.py`: generate canonical-source projections, lifecycle state separation, decision-ready briefs, and audience-specific views.
- `scripts/write_artifact_scaffold.py`: create nomia artifact scaffold.
- `scripts/validate_artifact.py`: dispatch canonical validator for one artifact.
- `scripts/validate_ops.py`: validate `ops.yaml`.
- `scripts/write_ops_scaffold.py`: create canonical `ops.yaml` with safe defaults and explicit collections.
- `scripts/validate_roadmap.py`: validate `roadmap.yaml` and `feature-map.yaml`.
- `scripts/validate_reporting.py`: validate `feature-report.md`, `release-notes.md`, optional `internal-notes.md`.
- `scripts/validate_portfolio.py`: validate `portfolio.yaml` and `portfolio.md`.
- `scripts/validate_human_artifacts.py`: validate heading/token-based markdown artifacts.
- `scripts/validate_contracts.py`: validate cross-skill contracts and actor write boundaries.
- `scripts/validate_board_paths.py`: validate canonical `BOARD_ROOT` placement.
- `scripts/normalize_human_artifacts.py`: normalize without inventing content.
- `scripts/nomia_utils.py`: shared helpers; import, do not run directly.

## Rules

Print clear errors/warnings. Exit non-zero on errors. Use scaffold writers and validators; do not leave template selection, template-backed writes, normalization, or validator selection to ad hoc judgment when a local script exists. Missing required artifacts are errors only when selected mode requires them. Unresolved `<...>` template tokens in generated artifacts are errors. Missing owners, stakeholders, target dates, and validation evidence warn unless schema requires the field. Never invent owners, dates, stakeholders, status, or evidence. Keep shared YAML, path, missing-value, and ISO-date helpers in `nomia_utils.py`; keep artifact-specific rules in their owning validators.

## Exit Behavior

`ERROR:` = required schema, enum, date, contract, or boundary violation; exit `1`. `WARNING:` = structurally usable but incomplete/risky; exit `0` when no errors. Normalization with `--check` exits `1` when files would change; without `--check`, rewrites formatting-safe content only.

## Commands

```bash
python <skill-root>/scripts/guide_intake.py path/to/intake.yaml --as-of 2026-07-21T12:00:00+00:00
python <skill-root>/scripts/evaluate_governance.py --handoff path/to/handoff.yaml --as-of 2026-07-21T12:00:00+00:00 --json-output path/to/handoff-result.json
python <skill-root>/scripts/project_governance_views.py path/to/ops.yaml --as-of 2026-07-21T12:00:00+00:00
python <skill-root>/scripts/write_artifact_scaffold.py path/to/status.md
python <skill-root>/scripts/validate_artifact.py path/to/status.md
python <skill-root>/scripts/validate_ops.py path/to/ops.yaml
python <skill-root>/scripts/write_ops_scaffold.py path/to/ops.yaml --spec-id spec-2026-04-20-sample-feature --spec-id-provenance user-supplied
python <skill-root>/scripts/validate_roadmap.py --roadmap path/to/roadmap.yaml --feature-map path/to/feature-map.yaml
python <skill-root>/scripts/validate_reporting.py --feature-report path/to/feature-report.md --release-notes path/to/release-notes.md --internal-notes path/to/internal-notes.md
python <skill-root>/scripts/validate_portfolio.py --portfolio-yaml path/to/portfolio.yaml --portfolio-md path/to/portfolio.md
python <skill-root>/scripts/validate_contracts.py --roadmap path/to/roadmap.yaml --feature-map path/to/feature-map.yaml --execution-evidence path/to/execution-evidence.yaml
python <skill-root>/scripts/validate_contracts.py --actor magia --changed-files path/to/changed-files.txt
python <skill-root>/scripts/validate_board_paths.py --changed-files path/to/changed-files.txt
python <skill-root>/scripts/normalize_human_artifacts.py path/to/ops.yaml path/to/feature-report.md
```

## Validator Coverage

Board-path validation checks nomia-owned artifact placement under `docs/boards/<board_id>/<year>/cycles/<cycle_id>/` or its `specs/<spec_id>/` packages, year/cycle consistency, canonical immutable ids, and board/spec artifact names in allowed locations.

Roadmap validation checks required fields, enums, feature-key format, dependency references, candidate spec consistency, and handoff boundary violations in `feature-map.yaml`.

Reporting validation checks required sections, audience, evidence, validation, rollout, deployment, rollback status, unsupported shipment/availability claims, internal-only or sensitive detail in `release-notes.md`, and unresolved unknown placeholders as warnings. Use `--mode feature-report`, `--mode release-notes`, or `--mode all`; default is `all`.
