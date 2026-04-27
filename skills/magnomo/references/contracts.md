# Contracts

Use for `validate-contracts` and any cross-skill boundary work.

Magnomo's contract is self-contained: validate paths and artifact shapes without loading or modifying Mago or Magia skill files.

## Actor Write Boundaries

`mago` may write Mago-owned planning artifacts and Mago skill references, including optional spec-scoped `technical-design.md` architecture planning artifacts. It must not write Magnomo artifacts, Magia execution evidence, or repository execution outputs.

`magia` may write repository code and Magia-owned execution evidence, plus controlled execution-state updates in Mago spec packages under the existing RALPH model. It must not write Magnomo artifacts, rewrite Mago planning intent, rewrite task definitions, or rewrite roadmap/product scope.

`magnomo` may write only Magnomo-owned governance, roadmap, RFC proposal, ADR record, reporting, portfolio artifacts, and Magnomo validation scripts/templates/examples. Repository-facing Magnomo artifacts must be placed only in their canonical board-scoped or spec-scoped locations from [canonical-paths.md](canonical-paths.md). It must not write Mago/Magia files, repository code, Mago planning packages, Mago `technical-design.md`, Magia execution records, or implementation task decomposition.

Run `scripts/validate_contracts.py --actor <actor> --changed-files <file>` against a newline-delimited changed-file list.

## Output Directories

Use `BOARD_ROOT` from [canonical-paths.md](canonical-paths.md) as the repository-facing root for Magnomo artifacts.

- Require `<board_id>` and `<cycle_version>` before writing files.
- Keep the values dynamic and use safe slug values, not literal placeholders.
- Place board-scoped artifacts directly in that directory.
- Place spec-scoped artifacts only in `BOARD_ROOT/specs/<spec_id>/`.
- Run `scripts/validate_board_paths.py` against changed files when path compliance matters.

## Magnomo-Owned Artifacts

Board-scoped: `portfolio.yaml`, `portfolio.md`, `roadmap.yaml`, `roadmap.md`, `rfc-proposals.md`, `adr-records.md`, `feature-map.yaml`, `release-notes.md`, and `internal-notes.md`.

Spec-scoped: `ops.yaml`, `status.md`, `stakeholder-brief.md`, `replanning.md`, and `feature-report.md`.

Mago-owned artifacts such as `prd.md`, `technical-design.md`, `tasks.md`, `validation.md`, and `notes.md` may be cited as linked evidence only when user-provided or already present.
