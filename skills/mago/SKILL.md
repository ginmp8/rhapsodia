---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction strategy, refactoring plans, architecture decisions, planned-decision records, execution handoff plans, tasks, validation plans, contract specs, migrations, observability, operations, security/risk notes, discovery, ordering, and define/refine workflows. do not use for execution work, delivery governance/status reporting, stakeholder communication, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Tech-lead planning skill. Convert nomia delivery intake plus repository evidence into canonical board/spec planning artifacts. MAGO plans intended design; it does not implement code, collect runtime evidence, deploy, commit, open PRs, or act as PO governance clerk.

## Scope and Ownership

Use only when output belongs under a resolved `BOARD_ROOT` for concrete `board_id`, `year`, and immutable `cycle_id`; package-scoped work also needs immutable `spec_id` under `BOARD_ROOT/specs/<spec_id>/` and a matching registration in the resolved board registry directory.

MAGO writes only canonical planning artifacts: cycle metadata, discovery state/index/candidate docs, per-spec registry records, generated catalog/queue projections, manifest, PRD, tasks, notes, validation, technical design, complexity-reduction plan, architecture decisions/ADRs, execution handoff plan, contract spec, migration strategy, observability design, operational requirements, security/risk considerations, and open questions. Legacy planning artifacts are normalized through `adapt`; legacy execution logs are not preserved in MAGO planning files and must be converted to current MAGIA-owned artifacts by MAGIA ADAPT before use as execution evidence.

MAGO must not write governance/status, stakeholder comms, release notes, roadmap bookkeeping, product-code diffs, runtime proof, execution notes/runbooks, migration execution notes, contract change notes, troubleshooting guides, Magia execution records, tests, commits, PRs, deployments, or noncanonical files. Decision artifacts created by MAGO are planned architecture or planned technical decisions only; execution-handoff artifacts are plans, not implementation evidence.

Routing: nomia owns request/governance facts; MAGO owns intended technical planning; Magia handles execution reality and execution-grounded docs. For mixed prompts, keep only the MAGO planning portion and hand off execution to Magia or governance/status work to nomia. Record unknowns as assumptions/blockers; never invent repository truth.

Governance RFC proposals, delivery status, stakeholder communication, release notes, portfolio reporting, and accepted business risk belong to nomia. MAGO may use RFC-style reasoning inside planning artifacts, but it must not create or update nomia governance RFC proposal logs or claim governance approval.

MAGO consumes Magia-owned execution evidence such as technical gap notes, implementation notes, validation evidence, or implementation ADRs only as read-only input for planning reconciliation. MAGO must not rewrite Magia evidence or turn it into runtime proof authored by MAGO.

A MAGO planning boundary is an authoring boundary, not an execution prohibition; execution-required tasks are valid planning outputs when they are bounded, evidence-backed, and explicitly require downstream Magia implementation plus a credible validation path.

For artifacts shared with MAGIA, load [references/shared-artifact-ownership.md](references/shared-artifact-ownership.md). MAGO owns planning definitions, validation plans, package intent, registry planning state, and canonical planning templates; MAGIA-created records cover execution evidence, implementation notes, task checkbox completion, and narrow technical execution-state sync backed by current evidence. Generated catalog and queue projections are never write targets for either skill. MAGO must preserve truthful MAGIA evidence and must not fabricate runtime results or completion state.

## Activation Policy

Activate only for creating, normalizing, auditing, or refining canonical repository planning artifacts. Strong triggers: refine nomia intake into a spec package; discover repository candidates; register or order backlog items without shared sequence counters; adapt legacy planning docs; prepare define-ready package shells; define/refine a package; write spec-scoped technical design; record planned ADRs; plan complexity reduction, simplification, de-abstraction, or refactoring; reshape tasks; define validation plans; split product-only from task-only planning.

Do not activate for code implementation, code edits, runtime tests, deployments, operational evidence, delivery governance, release notes, stakeholder status, portfolio reporting, or general docs outside `BOARD_ROOT`. If likely MAGO but `BOARD_ROOT`, `board_id`, `year`/`cycle_id`, or required `spec_id` is missing, stop before writing and ask for the smallest missing input.

## Required Inputs and Evidence

Resolve before writes: `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, required `spec_id`, evidence source, primary mode, and evidence payload. Derive paths through `references/canonical-paths.md`; use `references/concurrent-planning.md` for identity/registry rules; never create parallel planning trees or shared mutable sequence files.

Truth sources: repository contents, existing planning artifacts, nomia/roadmap handoff evidence, user context, and validated package state. Treat missing facts as assumptions/blockers. Load `references/evidence-contract.md` when claims depend on repository truth, execution/validation/dependency state, or traceability.

## Modes

Select exactly one primary mode before loading mode detail.

| Mode | Owns | Key validation |
|---|---|---|
| `discovery` | repository candidates and discovery state/index/candidate docs | `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` |
| `order` | independent per-spec registry records plus deterministic external catalog/queue projections | `scripts/validate_repo_board.py`; `scripts/validate_generated_view_contract.py` when projection contracts change |
| `adapt` | normalize drifted/legacy board/package artifacts into the canonical model | `scripts/validate_artifact.py` plus package/repo validators as applicable |
| `prepare-define` | seed define-ready package shells from one registry handoff | `scripts/validate_package.py`, `scripts/validate_repo_board.py` |
| `define` | full package: manifest, PRD, tasks, notes, validation, technical planning | `scripts/validate_package.py` |
| `refine` | update a full package without crossing mode boundaries | optional `scripts/normalize_package.py`, then `scripts/validate_package.py` |
| `technical-design` | architecture/contracts/ADRs/technical planning for one spec | `scripts/validate_technical_design.py` or `scripts/validate_artifact.py` |
| `complexity-reduction` | evidence-backed simplification/refactoring plan, task slices, validation expectations, ADRs for material trade-offs | `scripts/validate_artifact.py`, `scripts/validate_package.py`, static simplification-evidence review |
| `architecture-decision` | planned architecture decision/ADR | `scripts/validate_artifact.py` or static ADR review |
| `reshape-tasks` | task-plan reshaping/status alignment | `scripts/validate_artifact.py`, `scripts/validate_package.py` |
| `define-product` / `refine-product` | product docs only | `scripts/validate_artifact.py`, `scripts/validate_package.py` |
| `define-tasks` / `refine-tasks` | task plan only | `scripts/validate_artifact.py`; refine also runs normalization when useful, then package validation |

## Workflow and Progressive Loading

1. Select one primary mode; refuse primary-mode mixing.
2. Open `references/canonical-paths.md` and resolve `BOARD_ROOT` before writes.
3. Open `references/concurrent-planning.md` when creating, registering, ordering, deduplicating, or validating cycle/spec identities.
4. Open `references/common-planning.md`.
5. Open `references/technical-artifact-standards.md` for technical planning artifacts.
6. Open `references/complexity-reduction-planning.md` for simplification, de-abstraction, complexity reduction, or refactoring.
7. Open `references/architecture-decisions.md` and `references/adr-quality.md` for ADRs, planned decisions, or trade-offs.
8. Open exactly one primary mode file: `references/modes/discovery.md`, `references/modes/order.md`, `references/modes/adapt.md`, `references/modes/prepare-define.md`, `references/modes/define.md`, `references/modes/refine.md`, `references/modes/technical-design.md`, `references/modes/complexity-reduction.md`; architecture-decision uses `references/architecture-decisions.md`, `references/modes/reshape-tasks.md`, `references/modes/define-product.md`, `references/modes/refine-product.md`, `references/modes/define-tasks.md`, or `references/modes/refine-tasks.md`.
9. Open conditional refs only when triggered: `references/artifacts/discovery-order.md`, `references/artifacts/templates-and-status.md`, `references/artifacts/technical-design.md`, `references/markdown-writing.md`, `references/rfc-quality.md`, `references/specialist-spellbook.md`, `references/roadmap-evidence-input.md`, `references/operating-rules.md`, `references/activation-routing.md`, `references/planning-execution-handoff.md`, `references/shared-artifact-ownership.md`, `references/evidence-contract.md`, and `references/validation-and-packaging.md`.
10. Use scripts for identity creation, scaffolding, list updates, deterministic view rendering, normalization, validation, boundary checks, and package-level skill validation.
11. Use `assets/flows/discovery-order-prepare-define-loop.md` only for explicit multi-step discovery/order/prepare-define loops.
12. Review `examples/activation-scenarios.json` for activation/refusal evidence and `examples/hardening-scenarios.json` for package hardening boundary regression when needed.

## Template and Script Contract

Create cycle/spec identities only through `scripts/create_planning_identity.py`; it performs validation and atomic exclusive writes. Create/normalize template-backed package artifacts through scripts. Prefer `scripts/write_artifact_scaffold.py`; inspect `scripts/update_template_lists.py` with `--schema` before using it for supported list fields. Render the catalog and define-queue projections only with `scripts/render_registry_views.py` to a directory outside `BOARD_ROOT`; they are deterministic projections, not source-of-truth files.

Use these templates through scripts when their artifact is in scope: `assets/templates/cycle.yaml.template`, `assets/templates/spec-registry-entry.yaml.template`, `assets/templates/manifest.yaml.template`, `assets/templates/prd.md.template`, `assets/templates/tasks.md.template`, `assets/templates/notes.md.template`, `assets/templates/validation.md.template`, `assets/templates/technical-design.md.template`, `assets/templates/complexity-reduction-plan.md.template`, `assets/templates/adr.md.template`, `assets/templates/contract-spec.md.template`, `assets/templates/migration-strategy.md.template`, `assets/templates/observability-design.md.template`, `assets/templates/operational-requirements.md.template`, `assets/templates/security-and-risk-considerations.md.template`, `assets/templates/open-questions.md.template`, `assets/templates/discovery-state.json.template`, `assets/templates/discovery-index.yaml.template`, `assets/templates/discovery-candidate.md.template`, `assets/templates/spec-catalog.yaml.template`, `assets/templates/execution-handoff-plan.md.template`, and `assets/templates/define-queue.yaml.template`.

Package MAGO with `scripts/package_skill.py` after package gates pass. Script routing: artifact validation `scripts/validate_artifact.py`; package validation `scripts/validate_package.py`; board validation `scripts/validate_repo_board.py`; concurrent identity/dependency validation `scripts/validate_concurrent_board.py`; generated-view contract validation `scripts/validate_generated_view_contract.py`; technical design validation `scripts/validate_technical_design.py`; legacy normalization `scripts/normalize_package.py`; planning/execution handoff validation `scripts/validate_planning_execution_handoff.py`; source-truth claims `scripts/validate_evidence_contract.py`; blurred boundaries `scripts/validate_boundary.py`; activation routing `scripts/validate_activation_scenarios.py`; MAGO integrity `scripts/validate_skill_package.py`. Shared helpers are import-only in `scripts/mago_utils.py`; consuming validators provide CLI entrypoints and syntax checks cover helper changes.

Do not leave placeholders in completed artifacts unless creating a scaffold; replace dynamic fields with evidence-backed values or record assumptions, blockers, or open questions.

## Validation Gates

A run is incomplete until every touched artifact family has a validator outcome. Required gates: one primary mode; resolved `BOARD_ROOT`, `board_id`, `year`, and `cycle_id`; `spec_id` for package work; immutable IDs generated or validated rather than manually sequenced; writes stay under board/package/registry paths; no duplicate active `feature_key`; all spec dependencies resolve and the graph is acyclic; package identity matches registry identity; generated views reproduce deterministically when requested; supported templates are handled by scripts; planning facts are evidence-backed or unresolved; source-truth/traceability checks run when claims depend on repository truth; activation and boundary behavior are covered by examples during hardening/packaging. If a validator fails and cannot be fixed within MAGO planning scope, stop and report the blocker.

## Output Contract

Final responses include: selected mode and why it was the only primary mode; resolved `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, and package `spec_id` when applicable; touched artifacts grouped by canonical board/package/registry path; identity/scaffold/render/normalization/update/validator commands with pass/fail; relevant complexity diagnosis, simplification hypotheses, planned decisions, ADRs, assumptions, trade-offs, duplicate/dependency findings, unresolved questions; inputs/blockers recorded rather than invented; and handoff notes for requested execution/governance outside MAGO scope. Do not include product-code diffs, runtime proof, or noncanonical planning files.

## Stop Conditions

Stop before editing when mode selection requires mixing primary modes; required path identifiers are missing and cannot be derived; requested path is outside `BOARD_ROOT` or would duplicate a board tree; a requested write targets a legacy layout instead of adapting it; identity creation would overwrite an existing registry record; duplicate active cycle/feature work or dependency cycles cannot be resolved; the user asks for code implementation, task execution, runtime evidence, delivery governance, stakeholder comms, or release notes; simplification lacks repository evidence or explicit assumptions; technical decisions require current code/runtime evidence only Magia can produce; required template script/validator is unavailable and freehand structure would be needed; or validation fails and cannot be fixed in planning scope.

## Finalization Checklist

Before claiming completion: writes are under `BOARD_ROOT`, selected package path, or matching registry path; dynamic ids/status/dependencies/design/order decisions are evidence-backed or unresolved; registry files remain the source of truth and generated aggregates were not hand-edited; template-backed artifacts used scripts when supported; validators passed or blockers are reported; final response states commands, touched files, assumptions, decisions, and handoff boundaries.
