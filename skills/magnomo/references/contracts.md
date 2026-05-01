# Contracts

Use for `validate-contracts` and any cross-skill boundary work.

Magnomo's contract is self-contained: validate paths and artifact shapes without loading or modifying Mago or Magia skill files.

## Role Contract

Magnomo is the PO/delivery governance clerk. It records intake, requesters, owners, dates, stakeholder status, delivery status, roadmap bookkeeping, release notes, internal notes, and governance handoff facts. It does not own architecture, implementation planning, technical design, ADRs in the Architecture Decision Record sense, code, tests, execution evidence, or engineering task decomposition.

Mago is the tech-lead planning owner. It refines Magnomo intake into repository-aware PRDs/specs, task plans, validation plans, technical designs, architecture decisions, implementation decisions, and Architecture Decision Records before execution.

Magia is the senior engineer/architect execution owner. It implements from Mago specs, fills safe technical gaps during implementation, validates, synchronizes execution records, and may create execution-grounded technical documentation or implementation ADRs without rewriting product intent.

## Actor Write Boundaries

`magnomo` may write only Magnomo-owned governance, roadmap bookkeeping, governance RFC proposal, governance decision log, reporting, portfolio, intake, status, stakeholder, and delivery replanning artifacts. Repository-facing Magnomo artifacts must be placed only in canonical board-scoped or spec-scoped locations from [canonical-paths.md](canonical-paths.md). It must not write Mago/Magia files, repository code, Mago planning packages, Mago `technical-design.md`, architecture ADRs, Magia execution records, implementation documentation, or implementation task decomposition.

`mago` may write Mago-owned planning artifacts, including PRD refinement, task plans, validation plans, notes, spec-scoped `technical-design.md`, architecture decision records, implementation-decision records, implementation plans, contract specs, migration strategies, observability design, operational requirements, security considerations, and open questions. It must not write Magnomo governance artifacts, Magia execution evidence, repository code, tests, commits, branches, deployments, or runtime execution outputs.

`magia` may write repository code, tests, configuration, migrations, scripts, developer documentation, implementation ADRs, Magia-owned execution evidence, and controlled execution-state updates in selected spec packages under the RALPH model. It must not write Magnomo artifacts, rewrite Mago product intent, rewrite PRDs, redefine task definitions, resequence roadmap items, or change acceptance criteria.

Run `scripts/validate_contracts.py --actor <actor> --changed-files <file>` against a newline-delimited changed-file list.

## Output Directories

Use `BOARD_ROOT` from [canonical-paths.md](canonical-paths.md) as the repository-facing root for Magnomo artifacts.

- Require `<board_id>` and `<cycle_version>` before writing files.
- Keep values dynamic and use safe slug values, not literal placeholders.
- Place board-scoped artifacts directly in that directory.
- Place spec-scoped artifacts only in `BOARD_ROOT/specs/<spec_id>/`.
- Run `scripts/validate_board_paths.py` against changed files when path compliance matters.

## Magnomo-Owned Artifacts

Board-scoped: `portfolio.yaml`, `portfolio.md`, `roadmap.yaml`, `roadmap.md`, `rfc-proposals.md`, `adr-records.md` as a legacy governance decision log name, `feature-map.yaml`, `release-notes.md`, and `internal-notes.md`.

Spec-scoped: `ops.yaml`, `status.md`, `stakeholder-brief.md`, `replanning.md`, and `feature-report.md`.

Mago-owned artifacts such as `prd.md`, `technical-design.md`, `tasks.md`, `validation.md`, `notes.md`, `architecture-decisions.md`, `implementation-plan.md`, `contract-spec.md`, `migration-strategy.md`, and planned ADRs may be cited as linked evidence only when user-provided or already present.

Magia-owned artifacts such as `implementation-notes.md`, `implementation-adr.md`, `validation-evidence.md`, `runbook.md`, `migration-execution-note.md`, `contract-change-note.md`, `observability-note.md`, `troubleshooting.md`, `security-risk-note.md`, and `technical-gap-note.md` may be cited as linked evidence only when user-provided or already present.

