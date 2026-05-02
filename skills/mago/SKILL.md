---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction and simplification strategy, refactoring plans, architecture decisions, architecture decision records, implementation-decision records, implementation plans, tasks, validation plans, contract specs, migration strategies, observability design, operational requirements, security considerations, notes, discovery, ordering, and define/refine workflows. do not use for product governance/status reporting, stakeholder communication, code implementation, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Tech-lead planning skill. Convert Magnomo delivery intake and repository evidence into canonical board/spec planning artifacts: discovery, ordering, PRD refinement, technical design, complexity-reduction/refactoring plans, tasks, validation, contracts, migrations, observability, operational/security considerations, planned decisions, and ADRs. MAGO plans intended design; it does not implement code, collect runtime evidence, deploy, commit, open PRs, or act as PO governance clerk.

## Scope and Ownership

Use only when output belongs under a resolved `BOARD_ROOT` for concrete `board_id` and `cycle_version`; package-scoped work also needs `spec_id` under `BOARD_ROOT/specs/<spec_id>/`.

MAGO may create/update: discovery-state.json, discovery-index.yaml, candidate docs, spec-catalog.yaml, define-queue.yaml, manifest.yaml, prd.md, tasks.md, notes.md, validation.md, technical-design.md, complexity-reduction-plan.md, architecture-decisions.md, adrs/<adr_id>.md, implementation-plan.md, contract-spec.md, migration-strategy.md, observability-design.md, operational-requirements.md, security-and-risk-considerations.md, and open-questions.md.

MAGO must not write product governance/status, stakeholder comms, release notes, portfolio/roadmap bookkeeping, product-code diffs, runtime proof, implementation notes, executed runbooks, migration execution notes, contract change notes, troubleshooting guides, Magia execution records, tests, commits, PRs, deployments, or noncanonical planning files.

Routing: Magnomo owns request/governance facts; Mago owns intended technical planning; Magia owns implementation reality and execution-grounded docs. If a prompt crosses into execution, stop at planning and hand off to Magia. If it crosses into governance intake/status/roadmap/release comms, hand off to Magnomo. Record unknowns as assumptions/blockers; never invent repository truth.

## Activation Policy

Activate only for creating, normalizing, auditing, or refining canonical repository planning artifacts. Strong triggers: refine Magnomo intake into a spec package; discover repository candidates; order backlog into define queue; adapt legacy planning docs; prepare define-ready package shells; define/refine a package; write spec-scoped technical design; record planned architecture decisions/ADRs; plan complexity reduction, simplification, de-abstraction, or refactoring; reshape tasks; define validation plans; split product-only from task-only planning.

Do not activate for implementation, code edits, runtime tests, deployments, operational evidence, delivery governance, release notes, stakeholder status, portfolio reporting, or general docs outside `BOARD_ROOT`. For mixed prompts, keep only the MAGO planning portion and hand off the rest. For ambiguity, decide whether the requested output is a canonical MAGO artifact under `BOARD_ROOT`; otherwise do not use MAGO. If likely MAGO but `board_id`, `cycle_version`, `BOARD_ROOT`, or required `spec_id` is missing, stop before writing and ask for the smallest missing input.

## Required Inputs

Resolve before writes:

- `BOARD_ROOT`: supplied explicitly or derived through [references/canonical-paths.md](references/canonical-paths.md).
- `board_id`, `cycle_version`: concrete board path segments for board-scoped work.
- `spec_id`: required for package-scoped modes under `BOARD_ROOT/specs/<spec_id>/`.
- Evidence source: target repository or planning workspace.
- Mode intent and evidence payload: user request, Magnomo/roadmap handoff, repository evidence, existing artifacts, package state, or architecture-decision evidence.

If root/id/version cannot be derived safely, do not create parallel planning trees; ask the smallest blocker question or stop with the blocker named.

## Evidence Discipline

Truth sources: repository contents, existing planning artifacts, Magnomo handoff evidence, roadmap evidence, user context, and validated package state. Treat missing evidence as assumption/blocker. Do not infer hidden owner commitments, dependency state, implementation completion, validation results, production state, or Magia outcomes from names alone. Load [references/evidence-contract.md](references/evidence-contract.md) when claims depend on repository truth, execution/validation/dependency state, or traceability.

## Modes

Select exactly one primary mode before loading mode details.

- `discovery`: discover repository features/candidate work. Inputs: repo evidence, board id/version. Outputs: discovery state/index/candidate docs. Validate with `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` if board artifacts changed.
- `order`: order discovered or Magnomo-supplied candidates. Inputs: discovery/governance handoff plus ordering evidence. Outputs: spec catalog, define queue. Validate with `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py`.
- `adapt`: normalize drifted/legacy planning docs. Inputs: existing docs and canonical board path. Outputs: normalized board/package artifacts. Validate with `scripts/validate_artifact.py` plus package/repo validators as applicable.
- `prepare-define`: seed define-ready package shells. Inputs: define queue and selected spec ids. Outputs: package scaffolds under `BOARD_ROOT/specs/`. Validate with `scripts/validate_package.py` and `scripts/validate_repo_board.py`.
- `define`: define full spec package. Inputs: spec id plus roadmap/governance/repository evidence. Outputs: manifest, PRD, tasks, notes, validation, and required technical planning artifacts. Validate with `scripts/validate_package.py`.
- `refine`: refine full package without changing mode boundaries. Inputs: existing package plus requested planning corrections. Outputs: updated package artifacts. Run `scripts/normalize_package.py` when useful, then `scripts/validate_package.py`.
- `technical-design`: align architecture/contracts for one spec. Inputs: spec id and architecture evidence. Outputs: technical design, planned ADRs, contract spec, migration strategy, observability design, operational requirements, or security considerations. Validate with `scripts/validate_technical_design.py` or `scripts/validate_artifact.py`.
- `complexity-reduction`: plan simplification/refactoring. Inputs: spec id, repository evidence, complexity symptoms, behavior to preserve, risk tolerance. Outputs: complexity-reduction-plan.md, implementation plan, task slices, validation expectations, and ADRs only for material trade-offs. Validate with `scripts/validate_artifact.py`, `scripts/validate_package.py`, and static simplification-evidence review.
- `architecture-decision`: record a planned decision/ADR. Inputs: spec id, technical context, alternatives, owner/unknown, validation expectations. Outputs: architecture-decisions.md or spec ADR. Validate with `scripts/validate_artifact.py` or static ADR review.
- `reshape-tasks`: reshape task plans. Inputs: task plan evidence and selected package. Outputs: updated tasks and related status fields. Validate with `scripts/validate_artifact.py` and `scripts/validate_package.py`.
- `define-product` / `refine-product`: create/refine product docs only. Inputs: product evidence or existing product docs plus spec id. Outputs: product docs only. Validate with `scripts/validate_artifact.py` and `scripts/validate_package.py`.
- `define-tasks` / `refine-tasks`: create/refine tasks only. Inputs: product baseline or existing task plan, specialist needs/corrections. Outputs: task plan only. Validate with `scripts/validate_artifact.py`; for refine, run `scripts/normalize_package.py` when useful, then `scripts/validate_package.py`.

## Progressive Loading

1. Select one mode; refuse primary-mode mixing.
2. Open [references/canonical-paths.md](references/canonical-paths.md) and resolve `BOARD_ROOT` before writes.
3. Open [references/common-planning.md](references/common-planning.md).
4. Open [references/technical-artifact-standards.md](references/technical-artifact-standards.md) when technical planning artifacts are in scope.
5. Open [references/complexity-reduction-planning.md](references/complexity-reduction-planning.md) for simplification, de-abstraction, complexity reduction, or refactoring.
6. Open [references/architecture-decisions.md](references/architecture-decisions.md) and [references/adr-quality.md](references/adr-quality.md) for ADRs, implementation decisions, or trade-offs.
7. Open exactly one primary [references/modes/](references/modes/) file.
8. Open conditional refs only when triggered: [references/artifacts/discovery-order.md](references/artifacts/discovery-order.md), [references/artifacts/templates-and-status.md](references/artifacts/templates-and-status.md), [references/artifacts/technical-design.md](references/artifacts/technical-design.md), [references/markdown-writing.md](references/markdown-writing.md), [references/rfc-quality.md](references/rfc-quality.md), [references/specialist-spellbook.md](references/specialist-spellbook.md), [references/roadmap-evidence-input.md](references/roadmap-evidence-input.md), [references/operating-rules.md](references/operating-rules.md), [references/activation-routing.md](references/activation-routing.md), [references/planning-execution-handoff.md](references/planning-execution-handoff.md), [references/evidence-contract.md](references/evidence-contract.md), and [references/validation-and-packaging.md](references/validation-and-packaging.md).
9. Use [assets/templates/](assets/templates/) through scripts for supported artifacts; do not freehand template structure.
10. Use [assets/flows/discovery-order-prepare-define-loop.md](assets/flows/discovery-order-prepare-define-loop.md) only for explicit multi-step discovery/order/prepare-define flows.
11. Use [scripts/](scripts/) for scaffolding, list updates, normalization, validation, boundary checks, and package-level skill validation.
12. Review [examples/activation-scenarios.json](examples/activation-scenarios.json) when activation/refusal behavior needs scenario evidence.

## Template and Script Contract

Create/normalize template-backed artifacts through scripts. Prefer `scripts/write_artifact_scaffold.py`; use `scripts/update_template_lists.py` for supported list fields and inspect `--schema` first. Use [assets/templates/complexity-reduction-plan.md.template](assets/templates/complexity-reduction-plan.md.template) for simplification plans. Do not leave placeholders in completed artifacts unless creating a scaffold; replace dynamic fields with evidence-backed values or record assumption/blocker/open question.

Script routing:

- New template-backed files: `scripts/write_artifact_scaffold.py`.
- Supported lists: `scripts/update_template_lists.py`.
- Any touched artifact: `scripts/validate_artifact.py`.
- Package work: `scripts/validate_package.py`.
- Board work: `scripts/validate_repo_board.py`.
- Architecture artifacts: `scripts/validate_technical_design.py`.
- Mechanical legacy drift: `scripts/normalize_package.py`.
- Magia handoff artifacts: `scripts/validate_planning_execution_handoff.py`.
- Repository/source-truth claims: `scripts/validate_evidence_contract.py`.
- Blurred governance/execution boundaries: `scripts/validate_boundary.py`.
- Activation/mode routing: `scripts/validate_activation_scenarios.py`.
- MAGO package integrity: `scripts/validate_skill_package.py`.
- Build/archive MAGO: `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate` after package gates pass.

## Validation Gates

A run is incomplete until every touched artifact family has a validator outcome. Required gates: one primary mode; `BOARD_ROOT`, `board_id`, and `cycle_version` resolved before writes; `spec_id` for package work; writes stay under board/package path; supported templates handled by scripts; planning facts evidence-backed or recorded as unresolved; evidence/traceability validated when claims depend on repository truth; activation/boundary behavior covered by examples during hardening/packaging. If a validator fails and cannot be fixed within MAGO planning scope, stop and report blocker.

## Output Contract

Final response must include: selected mode and why it was the only primary mode; resolved `BOARD_ROOT`, `board_id`, `cycle_version`, and package `spec_id` when applicable; touched artifacts grouped by canonical board/package path; scaffold/normalization/update/validator commands with pass/fail; relevant complexity diagnosis, simplification hypotheses, planned decisions, ADRs, assumptions, trade-offs, unresolved questions; inputs/blockers recorded rather than invented; handoff note for requested execution/governance outside MAGO scope. Do not include product-code diffs, runtime proof, or noncanonical planning files.

## Stop Conditions

Stop before editing when: mode selection requires mixing primary modes; `BOARD_ROOT`, `board_id`, or `cycle_version` is missing and cannot be derived; requested path is outside `BOARD_ROOT` or would duplicate a board tree; user asks for code implementation, task execution, runtime evidence, delivery governance, stakeholder comms, or release notes; simplification would be based only on taste/naming without repository evidence or explicit assumptions; technical decision needs current code/runtime evidence only Magia can produce; required template script/validator is unavailable and freehand structure would be needed; validation fails and cannot be fixed in planning scope.

## Finalization Checklist

Before claiming completion: writes are under `BOARD_ROOT` or selected package path; dynamic ids/status/dependencies/design/order decisions are evidence-backed or unresolved; template-backed artifacts used scripts when supported; validators passed or blockers are reported; final response states commands, touched files, assumptions, decisions, and handoff boundaries.
