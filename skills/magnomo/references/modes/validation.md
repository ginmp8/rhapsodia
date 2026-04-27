# Validation

## Canonical Rules

- `BOARD_ROOT` is required when validation touches repository-facing Magnomo artifacts.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; otherwise derive it from `references/canonical-paths.md`.
- A selected spec path is required only when validation checks spec-scoped Magnomo artifacts.
- Keep validator ownership scoped to Magnomo artifacts and boundaries under `BOARD_ROOT` and selected spec packages.

Magnomo validators check Magnomo artifacts and ownership boundaries. They do not execute repository code, load Mago/Magia skill files, or infer missing facts.

## Scripts

- `scripts/write_artifact_scaffold.py`: create any Magnomo artifact scaffold from the canonical template workflow.
- `scripts/validate_artifact.py`: dispatch validation to the canonical Magnomo validator for the selected artifact.
- `scripts/validate_ops.py`: validate `ops.yaml`.
- `scripts/write_ops_scaffold.py`: create a canonical `ops.yaml` scaffold with safe defaults and explicit collection shapes.
- `scripts/validate_roadmap.py`: validate `roadmap.yaml` and `feature-map.yaml`.
- `scripts/validate_reporting.py`: validate `feature-report.md`, `release-notes.md`, and optional `internal-notes.md`.
- `scripts/validate_portfolio.py`: validate `portfolio.yaml` and `portfolio.md`.
- `scripts/validate_human_artifacts.py`: validate canonical Magnomo markdown artifacts that rely on headings and resolved placeholders.
- `scripts/validate_contracts.py`: validate cross-skill contracts and actor write boundaries.
- `scripts/validate_board_paths.py`: validate canonical `BOARD_ROOT` placement.
- `scripts/normalize_human_artifacts.py`: normalize Magnomo artifacts without inventing content.
- `scripts/magnomo_utils.py`: shared helpers for validators; import it from scripts, do not run it directly.

## Validation Rules

- Print clear errors and warnings.
- Return non-zero when errors are present.
- Use `scripts/write_artifact_scaffold.py` to start a new artifact from a template and `scripts/validate_artifact.py` to validate the result; do not leave template selection, template-backed writes, normalization, or validator selection to ad hoc LLM judgment when a local script exists.
- Treat missing required artifacts as errors only when the selected mode requires them.
- Treat unresolved template tokens such as `<...>` in generated artifacts as errors.
- Treat missing owners, stakeholders, target dates, and validation evidence as warnings unless the artifact schema requires the field.
- Never invent owners, dates, stakeholders, status, or evidence during validation or normalization.
- Reuse `scripts/magnomo_utils.py` for shared YAML loading, path normalization, message deduplication, missing-value checks, and ISO date handling. Keep artifact-specific rules inside the validator that owns them.

## Exit Behavior

- `ERROR:` lines mean the artifact violates a required schema, enum, date, contract, or write-boundary rule. The script exits with status `1`.
- `WARNING:` lines mean the artifact is structurally usable but incomplete or risky for human governance. The script exits with status `0` when no errors are present.
- Normalization with `--check` exits with status `1` when files would change; without `--check`, it rewrites only formatting-safe content.

## Commands

```bash
python .github/skills/magnomo/scripts/write_artifact_scaffold.py path/to/status.md
python .github/skills/magnomo/scripts/validate_artifact.py path/to/status.md
python .github/skills/magnomo/scripts/validate_ops.py path/to/ops.yaml
python .github/skills/magnomo/scripts/write_ops_scaffold.py path/to/ops.yaml --spec-id spec001
python .github/skills/magnomo/scripts/validate_roadmap.py --roadmap path/to/roadmap.yaml --feature-map path/to/feature-map.yaml
python .github/skills/magnomo/scripts/validate_reporting.py --feature-report path/to/feature-report.md --release-notes path/to/release-notes.md --internal-notes path/to/internal-notes.md
python .github/skills/magnomo/scripts/validate_portfolio.py --portfolio-yaml path/to/portfolio.yaml --portfolio-md path/to/portfolio.md
python .github/skills/magnomo/scripts/validate_contracts.py --roadmap path/to/roadmap.yaml --feature-map path/to/feature-map.yaml --execution-evidence path/to/execution-evidence.yaml
python .github/skills/magnomo/scripts/validate_contracts.py --actor magia --changed-files path/to/changed-files.txt
python .github/skills/magnomo/scripts/validate_board_paths.py --changed-files path/to/changed-files.txt
python .github/skills/magnomo/scripts/normalize_human_artifacts.py path/to/ops.yaml path/to/feature-report.md
```

## Board Path Validation

`scripts/validate_board_paths.py` checks:

- Magnomo-owned repository artifacts are under `BOARD_ROOT` or a selected spec package under `BOARD_ROOT/specs/<spec_id>/`.
- `<board_id>` and `<cycle_version>` are present and slug-safe.
- Spec-scoped artifacts use `specNNN` package ids.
- Board-scoped and spec-scoped artifact names appear only in their allowed canonical locations.

## Roadmap Validation

`scripts/validate_roadmap.py` checks:

- required roadmap and handoff fields
- enum values, feature-key format, dependency references, and candidate spec consistency
- handoff boundary violations in `feature-map.yaml`

## Reporting Validation

`scripts/validate_reporting.py` checks:

- required sections and audience
- evidence, validation, rollout, deployment, and rollback status
- unsupported release or availability claims
- internal-only or sensitive detail in `release-notes.md`
- unresolved unknown placeholders as warnings

Use `--mode feature-report`, `--mode release-notes`, or `--mode all` to choose which required artifacts are enforced. The default is `all`.
