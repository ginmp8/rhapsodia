# Contracts

Use for `validate-contracts` and cross-skill boundaries. nomia validates paths and artifact shapes without loading or modifying Mago or Magia skill files.

## Role Contract

nomia = PO/delivery governance clerk for intake, requesters, owners, dates, stakeholders, delivery status, roadmap bookkeeping, release notes, internal notes, and handoff facts. It does not own architecture, Mago technical execution planning, technical design, Architecture Decision Records, code, tests, execution evidence, or engineering task decomposition.

Mago = tech-lead planning owner for canonical cycle/spec identities, registry records, PRD/spec refinement, task plans, validation plans, technical designs, planned architecture decisions, planned technical decisions, and Architecture Decision Records before execution.

Magia = senior engineer/architect execution owner for implementation, validation, execution records, execution-grounded technical docs, implementation ADRs, runtime decisions, and narrow evidence-backed execution-state synchronization without rewriting product intent.

Handoff direction is explicit: nomia hands governance facts to Mago; Mago creates or selects immutable planning identities and hands execution-ready planning contracts to Magia; Magia returns execution evidence to Mago for technical replanning gaps and to nomia as read-only input for delivery reporting.

All three skills are independent packages. Shared path, identity, ownership, and handoff rules are duplicated as local contracts; no skill imports, executes, or requires another skill package at runtime.


## Mechanical Handoff Contract

Use `references/ecosystem-handoff-contract.json` as the normative machine contract and `scripts/ecosystem_handoff.py` as the only local producer/consumer interface. Nomia produces `nomia_to_mago`; it consumes `mago_to_nomia` and `magia_to_nomia` as attributed evidence. Each peer carries a byte-equivalent local copy, so no package imports or reads another package at runtime.

Every envelope carries schema and mapping versions, direction, source and target roles, source package version, observation time, provenance, freshness, payload, evidence references, unknowns, conflicts, and deterministic handoff identity. An accepted envelope authorizes only the receiving skill's existing role. It never authorizes Nomia to certify planning, execution, validation, release, or technical risk acceptance.

## Actor Write Boundaries

`nomia` may write only nomia governance, roadmap bookkeeping, governance RFC, governance decision log, reporting, portfolio, intake, status, stakeholder, and replanning artifacts. Repository-facing writes must be only in canonical board/spec locations from [canonical-paths.md](canonical-paths.md). It must not write Mago/Magia files, `cycle.yaml`, registry records, generated catalog/queue views, code, planning packages, technical designs, architecture ADRs, execution records, implementation docs, or implementation task decomposition.

`mago` may write Mago planning artifacts: cycle metadata, per-spec registry records, PRD refinement, task/validation plans, notes, spec-scoped `technical-design.md`, architecture decision records, planned technical decision records, execution handoff plans, contract specs, migration strategies, observability design, operational requirements, security considerations, and open questions. It must not write nomia artifacts, Magia evidence, code, tests, commits, branches, deployments, release notes, stakeholder status, or runtime outputs.

`magia` may write code, tests, config, migrations, scripts, developer docs, implementation ADRs, Magia execution evidence, and controlled execution-state updates in selected spec packages under RALPH. It may toggle only existing task checkboxes and synchronize only evidence-backed technical state in `manifest.yaml` and `registry/<spec_id>.yaml`. It must not write nomia artifacts, rewrite Mago product intent, rewrite PRDs, redefine task definitions, resequence roadmap items, or change acceptance criteria.

Validate with `scripts/validate_contracts.py --actor <actor> --changed-files <file>` against newline-delimited changed files.

## Output Directories

Use `BOARD_ROOT` from [canonical-paths.md](canonical-paths.md). Require `<board_id>`, `<year>`, and canonical `<cycle_id>` before writing. Use dynamic repository-truth values, not literal tokens. Board-scoped artifacts go directly under `BOARD_ROOT`; spec-scoped artifacts only under `BOARD_ROOT/specs/<spec_id>/`. A repository-facing `spec_id` must use `spec-YYYY-MM-DD-feature-key`, be supplied by the user, received through a handoff, or evidenced by an existing repository artifact, and retain that provenance. nomia does not create or modify package or registry identities. Run `scripts/validate_board_paths.py` when path compliance matters.

## nomia-Owned Artifacts

Board-scoped: `portfolio.yaml`, `portfolio.md`, `roadmap.yaml`, `roadmap.md`, `rfc-proposals.md`, `governance-decisions.md`, `feature-map.yaml`, `release-notes.md`, `internal-notes.md`.

Spec-scoped: `ops.yaml`, `status.md`, `stakeholder-brief.md`, `replanning.md`, `feature-report.md`.

Mago-owned artifacts (`cycle.yaml`, `registry/<spec_id>.yaml`, `manifest.yaml`, `prd.md`, `technical-design.md`, `tasks.md`, `validation.md`, `notes.md`, `architecture-decisions.md`, `execution-handoff-plan.md`, `contract-spec.md`, `migration-strategy.md`, planned ADRs) may be cited only as provided or existing evidence. `spec-catalog.yaml` and `define-queue.yaml`, when rendered externally, are disposable projections and never nomia write targets.

Magia-owned artifacts (`implementation-notes.md`, `implementation-adr.md`, `validation-evidence.md`, `runbook.md`, `migration-execution-note.md`, `contract-change-note.md`, `observability-note.md`, `troubleshooting.md`, `security-risk-note.md`, `technical-gap-note.md`) may be cited only as provided or existing evidence.

## RFC and Reporting Boundaries

nomia `rfc-proposal` is a governance proposal mechanism, not a technical design or implementation decision record. When a proposal depends on technical trade-offs, cite Mago planning evidence or Magia implementation evidence without copying their technical authority into the governance RFC.

nomia reporting artifacts may summarize validation state only as sourced evidence, for example `according to validation-evidence.md`. They must not claim that nomia validated code, tests, runtime behavior, deployment, or production readiness. Missing source evidence remains `unknown`, `pending`, `not recorded`, or `not released`.
