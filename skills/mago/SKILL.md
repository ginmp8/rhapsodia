---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction and simplification strategy, refactoring plans, architecture decisions, architecture decision records, implementation-decision records, implementation plans, tasks, validation plans, contract specs, migration strategies, observability design, operational requirements, security considerations, notes, discovery, ordering, and define/refine workflows. do not use for product governance/status reporting, stakeholder communication, code implementation, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

MAGO is the tech-lead planning skill. It converts Magnomo delivery intake into repository-aware implementation specifications, technical designs, complexity-reduction strategies, refactoring plans, task plans, validation plans, architecture decisions, and planned Architecture Decision Records. It does not implement code and does not operate as the PO governance clerk.

## Scope Boundary

MAGO owns repository planning artifacts under the canonical board model. Use it only when the output belongs under the resolved board root for a concrete `board_id` and `cycle_version`; package-scoped work also requires a concrete `spec_id`.

Owned outputs include discovery state, discovery index, discovery candidate docs, spec catalog, define queue, manifest, PRD refinement, task plan, notes, validation plan, spec-scoped technical design artifacts, complexity-reduction plans, refactoring strategies, architecture decisions, planned ADRs, implementation-decision records, implementation plans, contract specs, migration strategies, observability design, operational requirements, security considerations, and open technical questions.

Keep product governance, stakeholder status, release notes, portfolio reporting, roadmap bookkeeping, product-code changes, runtime execution evidence, deployments, commits, pull requests, and Magia execution records outside MAGO scope.

When a request crosses from planning into execution, stop at the planning boundary and hand off to Magia. When a request crosses into governance intake, stakeholder status, roadmap bookkeeping, or release communication, hand off to Magnomo. Record unknowns as planning assumptions or blockers; do not invent repository truth.

## Role Model

- Magnomo registers what was requested, who asked, when it is needed, stakeholders, delivery state, and governance handoff facts.
- Mago acts like the tech lead: refines the request into technical intent, PRD alignment, technical design, complexity-reduction strategy, tasks, validation, trade-offs, planned architecture decisions, and ADRs.
- Magia acts like the senior engineer/architect: implements from Mago artifacts, validates, updates execution records, and may create execution-grounded technical documentation when implementation reveals new facts.

## Technical Planning Artifact Ownership

MAGO documents intended design. MAGIA documents implementation reality.

MAGO may create or update:

- technical-design.md: intended architecture and component design.
- complexity-reduction-plan.md: planned simplification or de-abstraction strategy, including evidence, target seams, phases, validation, rollback, and handoff to Magia.
- architecture-decisions.md or adrs/<adr_id>.md: planned architecture decisions and ADRs.
- implementation-plan.md: planned implementation strategy before code changes.
- tasks.md: task decomposition suitable for Magia execution.
- validation.md: validation plan and acceptance checks Magia must prove.
- contract-spec.md: intended API/event/schema/file/interface contracts.
- migration-strategy.md: planned migration, compatibility, rollout, and rollback strategy.
- observability-design.md: required logs, metrics, traces, dashboards, and alerts.
- operational-requirements.md: expected runbook needs, reprocessing, support, and operability requirements.
- security-and-risk-considerations.md: planned security, data, PII, secrets, auth, compliance, and risk constraints.
- open-questions.md: unresolved technical questions or blockers before execution.

MAGO must not write implementation notes, validation evidence, runbooks as executed operation, migration execution notes, contract change notes, troubleshooting guides, Magia execution records, repository code, tests, commits, or deployments.

## Activation Policy

Activate MAGO only when the user is asking to create, normalize, audit, or refine repository planning artifacts that belong in the canonical board model. Strong positive triggers include refining Magnomo intake into a spec package, discovery of repository candidates, ordering a backlog into the define queue, adapting legacy planning docs, preparing define-ready package shells, defining or refining a spec package, producing a spec-scoped technical design, recording planned architecture decisions or ADRs, planning complexity reduction, simplifying over-engineered designs, de-abstracting unnecessary layers, reshaping tasks, defining validation plans, and separating product-only and task-only planning.

Do not activate MAGO for implementation, product-code edits, runtime testing, deployment, operational evidence collection, delivery governance, release notes, stakeholder status, portfolio reporting, or general documentation outside the resolved board root. When a prompt mixes planning with execution or governance, keep only the planning portion in MAGO scope and hand off the rest instead of creating execution or governance artifacts.

For ambiguous prompts, first decide whether the requested output is a canonical MAGO artifact under BOARD_ROOT. If not, do not use MAGO. If the user likely wants MAGO but omits `board_id`, `cycle_version`, `BOARD_ROOT`, or `spec_id` needed by the selected mode, stop before writing and ask for the smallest missing input.

## Required Inputs

Resolve these inputs before writing or changing any MAGO artifact:

- `BOARD_ROOT`: active canonical board root resolved through [references/canonical-paths.md](references/canonical-paths.md) or supplied explicitly.
- `board_id` and `cycle_version`: required concrete path segments for board-scoped work.
- `spec_id`: required for package-scoped modes under `BOARD_ROOT/specs/<spec_id>/`.
- Target repository or planning workspace: the evidence source used to inspect existing planning artifacts.
- Mode intent and evidence payload: user request, Magnomo intake or roadmap handoff, repository evidence, artifact content, package state, or architecture decision evidence needed for the selected mode.

If the board root, board id, or cycle version cannot be derived safely, do not create parallel planning files. Ask the smallest missing-input question or stop with the blocker named explicitly.

## Evidence Discipline

Use repository contents, existing planning artifacts, Magnomo handoff evidence, roadmap evidence, user-provided context, and validated package state as truth sources. Treat absent evidence as an unresolved assumption or blocker. Do not infer hidden repository facts, owner commitments, dependency status, implementation completion, validation results, production state, or Magia execution outcomes from naming conventions alone.

Load [references/evidence-contract.md](references/evidence-contract.md) when planning claims depend on repository truth, execution state, validation state, dependency state, or source traceability.

## Mode Selection Matrix

Choose exactly one primary mode before loading mode details.

| User intent | Mode | Required inputs | Primary outputs | Final validator |
|---|---|---|---|---|
| discover repository features or candidate work | `discovery` | repo evidence, board id, cycle version | discovery state, discovery index, discovery candidate docs | `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` if board artifacts changed |
| order discovered or Magnomo-supplied candidates into the backlog | `order` | discovery or governance handoff artifacts, ordering evidence | spec catalog and define queue | `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` |
| adapt drifted or legacy planning docs into canonical board shape | `adapt` | existing planning docs, canonical board path | normalized board or package artifacts | `scripts/validate_artifact.py`, package or repo validators as applicable |
| seed define-ready package shells from ordered work | `prepare-define` | define queue, selected spec ids | package scaffolds under `BOARD_ROOT/specs/` | `scripts/validate_package.py` and `scripts/validate_repo_board.py` |
| define a full spec package | `define` | spec id, roadmap/governance/repository evidence | manifest, PRD, tasks, notes, validation, and required technical planning artifacts | `scripts/validate_package.py` |
| refine a full spec package without changing mode boundaries | `refine` | existing package, requested planning corrections | updated package artifacts | `scripts/normalize_package.py` when useful, then `scripts/validate_package.py` |
| align architecture or contracts for one selected spec | `technical-design` | spec id, architecture evidence | technical design, planned ADRs, contract spec, migration strategy, observability design, operational requirements, or security considerations | `scripts/validate_technical_design.py` or `scripts/validate_artifact.py` |
| plan complexity reduction or simplification | `complexity-reduction` | spec id, repository evidence, complexity symptoms, behavior to preserve, risk tolerance | complexity-reduction-plan.md, implementation plan, task slices, validation expectations, and ADRs only when architectural trade-offs are material | `scripts/validate_artifact.py`, `scripts/validate_package.py`, and static review of simplification evidence |
| record a planned architecture decision or ADR | `architecture-decision` | spec id, technical context, alternatives, owner/unknown, validation expectations | architecture-decisions.md or spec-scoped ADR file | `scripts/validate_artifact.py` or static ADR quality check |
| reshape broad task plans into canonical task structure | `reshape-tasks` | task plan evidence, selected package | updated task plan and related status fields | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| define product-only artifacts | `define-product` | product evidence, spec id | product docs only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| refine product-only artifacts | `refine-product` | existing product docs, requested corrections | updated product docs only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| define task-only artifacts | `define-tasks` | product baseline, task evidence, specialist needs | task plan only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| refine task-only artifacts | `refine-tasks` | existing task plan, requested corrections | updated task plan only | `scripts/normalize_package.py` when useful, then `scripts/validate_package.py` |

## Progressive Loading Workflow

1. Select one mode from the matrix and refuse mode mixing.
2. Open [references/canonical-paths.md](references/canonical-paths.md) and resolve `BOARD_ROOT` before any write.
3. Open [references/common-planning.md](references/common-planning.md) for shared planning rules.
4. Open [references/technical-artifact-standards.md](references/technical-artifact-standards.md) when technical planning artifacts are in scope.
5. Open [references/complexity-reduction-planning.md](references/complexity-reduction-planning.md) when the request involves reducing complexity, removing unnecessary abstractions, simplifying architecture, de-abstracting layers, or planning refactors.
6. Open [references/architecture-decisions.md](references/architecture-decisions.md) and [references/adr-quality.md](references/adr-quality.md) when ADRs, implementation decisions, or trade-offs are in scope.
7. Open exactly one primary mode reference from [references/modes/](references/modes/): `discovery`, `order`, `adapt`, `prepare-define`, `define`, `refine`, `technical-design`, `complexity-reduction`, `reshape-tasks`, `define-product`, `refine-product`, `define-tasks`, or `refine-tasks`.
8. Open additional references only when their condition applies:
   - [references/artifacts/discovery-order.md](references/artifacts/discovery-order.md) for discovery, ordering, or define-handoff structure.
   - [references/artifacts/templates-and-status.md](references/artifacts/templates-and-status.md) for package structure, status fields, or template-backed artifact consistency.
   - [references/artifacts/technical-design.md](references/artifacts/technical-design.md) for spec-scoped architecture alignment.
   - [references/markdown-writing.md](references/markdown-writing.md) for Markdown quality.
   - [references/rfc-quality.md](references/rfc-quality.md) for PRD assumptions, options, and unresolved decisions.
   - [references/specialist-spellbook.md](references/specialist-spellbook.md) for task specialist metadata.
   - [references/roadmap-evidence-input.md](references/roadmap-evidence-input.md) for roadmap-sourced define or refine work.
   - [references/operating-rules.md](references/operating-rules.md) when scope, handoff, or artifact ownership is ambiguous.
   - [references/activation-routing.md](references/activation-routing.md) when activation, negative triggers, ambiguous routing, regression, or adversarial routing need scenario-backed review.
   - [references/planning-execution-handoff.md](references/planning-execution-handoff.md) when preparing executable handoff to Magia.
   - [references/evidence-contract.md](references/evidence-contract.md) when repository facts, traceability, execution-state, validation-state, dependency-state, or source-of-truth claims need explicit evidence controls.
   - [references/validation-and-packaging.md](references/validation-and-packaging.md) before final package validation or when validating the skill package itself.
9. Use [assets/templates/](assets/templates/) through scripts rather than freehand copying whenever creating supported artifacts.
10. Use [assets/flows/discovery-order-prepare-define-loop.md](assets/flows/discovery-order-prepare-define-loop.md) only for multi-step planning flows that explicitly stay within discovery, ordering, and define-preparation boundaries.
11. Use [scripts/](scripts/) for scaffolding, list updates, normalization, artifact validation, board validation, boundary checks, and package-level skill validation.
12. Review [examples/activation-scenarios.json](examples/activation-scenarios.json) when activation or refusal behavior needs scenario evidence.

## Template Asset Contract

Use template-backed artifact creation instead of freehand structure whenever a supported artifact is created or normalized. Prefer `scripts/write_artifact_scaffold.py` for new files and `scripts/update_template_lists.py` for supported list fields. Use [assets/templates/complexity-reduction-plan.md.template](assets/templates/complexity-reduction-plan.md.template) when creating a planned simplification artifact.

Do not copy template placeholders into final artifacts unless the selected mode explicitly creates a scaffold. For completed planning artifacts, replace dynamic fields with evidence-backed values or record the unresolved value as an assumption, blocker, or open question.

## Script Routing

- Create new template-backed artifacts with ``scripts/write_artifact_scaffold.py`.
- Populate supported list fields with `scripts/update_template_lists.py`; check supported schemas with its `--schema` option before editing by hand.
- Validate any touched MAGO artifact with `scripts/validate_artifact.py` so validator selection is mechanical.
- Validate package-scoped work with `scripts/validate_package.py`.
- Validate board-scoped work with `scripts/validate_repo_board.py`.
- Validate spec-scoped architecture artifacts with `scripts/validate_technical_design.py`.
- Normalize legacy package drift with `scripts/normalize_package.py` when the change is mechanical and evidence-preserving.
- Validate planning/execution handoff with `scripts/validate_planning_execution_handoff.py` when Magia handoff artifacts are created or changed.
- Validate package evidence and traceability with `scripts/validate_evidence_contract.py` when touched artifacts include repository facts, execution-state, validation-state, dependency-state, or source-of-truth claims.
- Run `scripts/validate_boundary.py` when changes could blur MAGO planning boundaries with governance or execution workflows.
- Validate activation and mode-routing scenarios with `scripts/validate_activation_scenarios.py` during hardening or packaging.
- Validate MAGO skill package integrity with `scripts/validate_skill_package.py` during hardening or packaging.
- Build and archive MAGO itself with `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate` only after package-level gates pass.

## Validation Gates

A MAGO run is incomplete until every touched artifact family has an explicit validator outcome. Use script output as measured evidence only when the command was actually run. If a validator fails and the failure cannot be corrected within MAGO planning scope, stop and report the blocker.

Required gates are: exactly one primary mode selected; BOARD_ROOT, board_id, and cycle_version resolved before writes; spec_id resolved for package-scoped work; all writes stay under BOARD_ROOT or the selected package; template-backed artifacts are created or normalized through scripts when supported; referenced planning facts are evidence-backed or recorded as unresolved; evidence and traceability are validated when package claims depend on repository truth; activation and boundary behavior remains covered by examples/activation-scenarios.json during hardening or packaging.

## Output Contract

For every in-scope MAGO run, the final response must include:

- selected mode and why it was the only primary mode used;
- resolved `BOARD_ROOT`, `board_id`, `cycle_version`, and `spec_id` when package-scoped;
- touched artifacts grouped by canonical board or package path;
- scaffold, normalization, update, and validator commands run, with pass or fail outcome;
- complexity-reduction diagnosis, simplification hypotheses, planned architecture decisions, ADRs, assumptions, trade-offs, and unresolved questions when relevant;
- unresolved inputs, assumptions, or blocked changes recorded in planning artifacts instead of invented;
- handoff note when the user requested implementation, execution evidence, or governance outside MAGO scope.

Do not include product-code diffs, runtime execution proof, or non-canonical planning files as MAGO output.

## Stop Conditions

Stop before editing when any condition applies:

- the active mode cannot be selected without mixing primary modes;
- `BOARD_ROOT`, `board_id`, or `cycle_version` is missing and cannot be derived;
- a requested artifact path is outside the resolved board root or would create a duplicate board tree;
- the user asks for implementation code, task execution, runtime evidence, delivery governance, stakeholder communication, or release notes;
- a complexity-reduction plan would be based only on taste, preference, or naming complaints without repository evidence or explicit assumptions;
- a technical decision requires current code/runtime evidence that only Magia can truthfully produce;
- a required template script or validator is unavailable and the change would require freehanding template structure;
- validation fails and cannot be fixed within MAGO planning scope.

## Finalization Checklist

Before claiming completion:

- all writes are under `BOARD_ROOT` or the selected package path;
- every dynamic id, status, dependency, design choice, and ordering decision is evidence-backed or recorded as unresolved;
- template-backed artifacts were created or updated through scripts when supported;
- validators for the touched artifact family passed, or failures are reported as blockers;
- final response reports commands, touched files, assumptions, decisions, and handoff boundaries.
