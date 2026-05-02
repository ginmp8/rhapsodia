# Contracts

Use for `validate-contracts` and cross-skill boundaries. Magnomo validates paths and artifact shapes without loading or modifying Mago or Magia skill files.

## Role Contract

Magnomo = PO/delivery governance clerk for intake, requesters, owners, dates, stakeholders, delivery status, roadmap bookkeeping, release notes, internal notes, and handoff facts. It does not own architecture, Mago technical execution planning, technical design, Architecture Decision Records, code, tests, execution evidence, or engineering task decomposition.

Mago = tech-lead planning owner for PRD/spec refinement, task plans, validation plans, technical designs, planned architecture decisions, planned technical decisions, and Architecture Decision Records before execution.

Magia = senior engineer/architect execution owner for implementation, validation, execution records, execution-grounded technical docs, implementation ADRs, and runtime decisions, without rewriting product intent.

Handoff direction is explicit: Magnomo hands governance facts to Mago; Mago hands execution-ready planning contracts to Magia; Magia returns execution evidence to Mago for technical replanning gaps and to Magnomo as read-only input for delivery reporting.

## Actor Write Boundaries

`magnomo` may write only Magnomo governance, roadmap bookkeeping, governance RFC, governance decision log, reporting, portfolio, intake, status, stakeholder, and replanning artifacts. Repository-facing writes must be only in canonical board/spec locations from [canonical-paths.md](canonical-paths.md). It must not write Mago/Magia files, code, Mago planning packages, Mago `technical-design.md`, architecture ADRs, Magia execution records, implementation docs, or implementation task decomposition.

`mago` may write Mago planning artifacts: PRD refinement, task/validation plans, notes, spec-scoped `technical-design.md`, architecture decision records, planned technical decision records, execution handoff plans, contract specs, migration strategies, observability design, operational requirements, security considerations, and open questions. It must not write Magnomo artifacts, Magia evidence, code, tests, commits, branches, deployments, release notes, stakeholder status, or runtime outputs.

`magia` may write code, tests, config, migrations, scripts, developer docs, implementation ADRs, Magia execution evidence, and controlled execution-state updates in selected spec packages under RALPH. It must not write Magnomo artifacts, rewrite Mago product intent, rewrite PRDs, redefine task definitions, resequence roadmap items, or change acceptance criteria.

Validate with `scripts/validate_contracts.py --actor <actor> --changed-files <file>` against newline-delimited changed files.

## Output Directories

Use `BOARD_ROOT` from [canonical-paths.md](canonical-paths.md). Require `<board_id>` and `<cycle_version>` before writing. Use dynamic safe slug values, not literal placeholders. Board-scoped artifacts go directly under `BOARD_ROOT`; spec-scoped artifacts only under `BOARD_ROOT/specs/<spec_id>/`. Run `scripts/validate_board_paths.py` when path compliance matters.

## Magnomo-Owned Artifacts

Board-scoped: `portfolio.yaml`, `portfolio.md`, `roadmap.yaml`, `roadmap.md`, `rfc-proposals.md`, `governance-decisions.md`, `feature-map.yaml`, `release-notes.md`, `internal-notes.md`.

Spec-scoped: `ops.yaml`, `status.md`, `stakeholder-brief.md`, `replanning.md`, `feature-report.md`.

Mago-owned artifacts (`prd.md`, `technical-design.md`, `tasks.md`, `validation.md`, `notes.md`, `architecture-decisions.md`, `execution-handoff-plan.md`, `contract-spec.md`, `migration-strategy.md`, planned ADRs) may be cited only as provided or existing evidence.

Magia-owned artifacts (`implementation-notes.md`, `implementation-adr.md`, `validation-evidence.md`, `runbook.md`, `migration-execution-note.md`, `contract-change-note.md`, `observability-note.md`, `troubleshooting.md`, `security-risk-note.md`, `technical-gap-note.md`) may be cited only as provided or existing evidence.

## RFC and Reporting Boundaries

Magnomo `rfc-proposal` is a governance proposal mechanism, not a technical design or implementation decision record. When a proposal depends on technical trade-offs, cite Mago `technical-design.md`, Mago planned ADRs, Magia `implementation-adr.md`, `implementation-notes.md`, or `validation-evidence.md` as evidence without copying their technical authority into the governance RFC.

Magnomo reporting artifacts may summarize validation state only as sourced evidence, for example `according to validation-evidence.md`. They must not claim that Magnomo validated code, tests, runtime behavior, deployment, or production readiness. Missing source evidence remains `unknown`, `pending`, `not recorded`, or `not released`.
