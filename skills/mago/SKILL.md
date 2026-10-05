---
name: mago
description: use when asked to plan, normalize, audit, define, refine, reconcile, or prepare tech-lead owned repository planning artifacts from governance intake, repository evidence, or existing mago state. covers prds, technical designs, planned adrs, refactoring/complexity-reduction plans, tasks, validation plans, contracts, migrations, observability, operations, security/risk notes, discovery, ordering, and execution handoffs. do not use for product-code implementation, runtime tests/evidence, deployments, commits/prs, delivery governance/status, release communication, stakeholder reporting, or magia execution records.
---

# MAGO

## Selection and authority

Mago owns intended technical planning and canonical Mago planning artifacts. It may inspect repository/runtime-adjacent evidence needed to plan, but it never changes product code, executes product tests/deployments, owns delivery governance, accepts business risk, or fabricates runtime proof. Route execution to Magia and delivery/governance ownership to Nomia. Use [activation routing](references/activation-routing.md) for ambiguous or mixed requests.

- Nomia owns requester/owner/dates, `business_priority`, stakeholders, roadmap/governance status, closure, and release communication.
- Mago owns requirements, designs, planned decisions/tasks/validation, `technical_criticality`, `execution_sequence`, technical risk, and execution handoff.
- Magia owns implementation, tests, runtime validation, execution decisions, and execution evidence.
- A Mago planning boundary is an authoring boundary; execution-required tasks are valid planning outputs when bounded, assigned to Magia, and linked to planned validation. Mago never executes them.
- Reject mixed ecosystem versions before mutation, unsupported envelope schemas, wrong-owner fields, privacy/content contradictions, absent durable-artifact privacy lineage, false authenticity claims, and legacy switches not explicitly selected.

## Default operating profile and required inputs

`artifact-native` is the default. Resolve `repo_root`, Mago artifact root, stable `work_item_id`/planning identity, evidence source, rigor profile, lifecycle stage, exactly one mode, and payload before writes. Native operation requires no Board, cycle, shared registry, Workspace, UI, or peer package. Use [artifact-native operation](references/artifact-native.md); for a new native spec create identity with `scripts/native_planning.py identity` and reuse it immutably.

`legacy-board` is opt-in compatibility only. Presence of Board files never selects it automatically. In any mode/reference document, instructions involving `BOARD_ROOT`, `board_id`, `cycle_id`, registry files, manifests, catalog/queue projections, or Board-specific scripts apply only after `legacy-board` is explicitly selected. For that branch use [common planning](references/common-planning.md), [canonical paths](references/canonical-paths.md), [operating rules](references/operating-rules.md), and [concurrent planning](references/concurrent-planning.md). If a selected mode documents only Board-specific write mechanics and `legacy-board` was not selected, do not invent a native path: remain read-only or block until the native contract supplies one.

Read-only mode selection/blocker diagnosis may occur before all write inputs are resolved; mutation may not. Preserve unknowns and use current owner sources, typed handoffs, repository evidence, and validated planning evidence; never invent technical, validation, privacy, dependency, status, or readiness truth. Apply [evidence rules](references/evidence-contract.md).

## Public workflow and rigor

Sequence: `clarify -> define -> analyze -> handoff -> reconcile`. Choose one [profile/lifecycle](references/profiles-and-lifecycle.md): `quick` only for bounded reversible low-risk work; `standard` normally; `governed` for regulatory, privacy/security, contract/schema, migration, irreversible-data, operational, cross-service, or multi-repository impact. Standard/governed work applies [requirements/traceability](references/requirements-and-traceability.md), [clarification readiness](references/clarification-readiness.md), and [clarification prioritization](references/clarification-prioritization.md), preserving `REQ -> AC -> DECISION -> TASK -> VALIDATION`. Use [getting started](references/getting-started.md) only when the entrypoint or next planning step is unclear.

## Internal mode router

| Intent | Mode |
|---|---|
| repository discovery | [discovery](references/modes/discovery.md) |
| deduplicate/register/order planning candidates | [order](references/modes/order.md) |
| legacy/drift normalization | [adapt](references/modes/adapt.md) |
| seed/full planning package | [prepare-define](references/modes/prepare-define.md), [define](references/modes/define.md), [refine](references/modes/refine.md) |
| product-only or task-only planning | [define-product](references/modes/define-product.md), [refine-product](references/modes/refine-product.md), [define-tasks](references/modes/define-tasks.md), [refine-tasks](references/modes/refine-tasks.md) |
| architecture/contracts/migration/ops/security design | [technical-design](references/modes/technical-design.md) |
| behavior-preserving simplification plan | [complexity-reduction](references/modes/complexity-reduction.md) |
| planned architecture decision | [architecture decisions](references/architecture-decisions.md) |
| task reshaping or plan/evidence reconciliation | [reshape-tasks](references/modes/reshape-tasks.md), [reconcile](references/modes/reconcile.md) |

## Planning sequence

1. Route non-Mago work; resolve owner-scoped identity, operating profile, lifecycle stage, rigor profile, and exactly one mode.
2. Native branch: load [artifact-native operation](references/artifact-native.md) plus the selected mode. Legacy branch: load [common planning](references/common-planning.md) plus the selected mode. Do not import legacy storage mechanics into native planning.
3. Select only evidence-triggered artifacts with the [decision matrix](references/artifact-decision-matrix.md); templates never trigger writes by themselves.
4. Apply triggered quality contracts directly: [technical standards](references/technical-artifact-standards.md), [ADR quality](references/adr-quality.md), [security-risk v2](references/security-risk-contract.md), [priority ownership](references/priority-contract.md), and [shared artifact ownership](references/shared-artifact-ownership.md).
5. Load branch resources directly when triggered: [discovery/order artifacts](references/artifacts/discovery-order.md), [templates/status](references/artifacts/templates-and-status.md), [technical-design artifact](references/artifacts/technical-design.md), [complexity reduction](references/complexity-reduction-planning.md), [Markdown rules](references/markdown-writing.md), and [specialist metadata](references/specialist-spellbook.md).
6. Existing specs require a [change delta](references/change-delta.md). External formats use [interoperability](references/interoperability-and-reconciliation.md) plus the [adapter contract](references/adapter-development-contract.md); disclose loss and keep projections non-authoritative.
7. Multi-file writes use the [transaction/resume contract](references/mutation-transaction-and-resume.md) and `scripts/mutation_transaction.py`: stage, validate, atomically promote, detect drift, and verify rollback.
8. Validate the selected artifacts and publication, hand off only validated intent, and reconcile Magia evidence read-only with provenance; legacy execution evidence must be normalized by Magia before Mago treats it as current. Optional read-only projections: [planning compass](references/planning-compass.md) via `scripts/render_planning_compass.py`, [execution waves](references/execution-wave-projection.md) via `scripts/render_execution_waves.py`, and [brownfield summary](references/brownfield-discovery-summary.md).

## Ecosystem, portability, and validation invariants

The Agent Skills package is the host-neutral semantic core; `agents/openai.yaml` is optional. Resolve `<PYTHON>` to Python 3.11+ and use package-relative/capability-based execution; core behavior must not require Bash, fixed install paths, vendor-private APIs, or peer-package runtime imports.

This package participates in ecosystem release `2.0.0` with shared-contract version `1.0.0`. Use [ecosystem ownership](references/ecosystem-ownership-contract.json), [reproducibility](references/ecosystem-reproducibility-contract.json), frozen [cross-skill scenarios](evals/ecosystem-cross-skill-scenarios.json), [routing](references/ecosystem-routing-contract.md), [lifecycle](references/ecosystem-lifecycle.md), and the strict [ecosystem handoff contract](references/ecosystem-handoff-contract.md) through `scripts/ecosystem_handoff.py`. Perform only the current Mago phase, preserve repeated phases, then hand off. Consume `nomia_to_mago`/`magia_to_mago`; produce `mago_to_magia`/`mago_to_nomia`. `scripts/validate_ecosystem_reproducibility.py` must remain package-local and peer-independent; `scripts/route_ecosystem_request.py` is read-only and `scripts/handoff_ledger.py` stores transport state only. Package receipts bind baseline, frozen candidate, shared-contract, and archive hashes without creating runtime peer coupling.

Write only within the resolved Mago artifact root. For native work use `scripts/native_planning.py` and `scripts/native_artifacts.py`; `scripts/create_planning_identity.py` and `scripts/write_artifact_scaffold.py` are legacy-board adapters. Run the narrowest relevant validators. Package validation must include `scripts/validate_artifact_matrix.py references/artifact-decision-matrix.md` and `scripts/validate_planning_experience.py`; governed work requires current traceability/quality and security v2 when triggered. Use [roadmap evidence](references/roadmap-evidence-input.md), [RFC quality](references/rfc-quality.md), [planning/execution handoff](references/planning-execution-handoff.md), [validation/packaging](references/validation-and-packaging.md), and [installation/release](references/installation-and-release.md) only when their decision is active. Package only after local, contract, provenance, routing, lifecycle, recovery, privacy, and distribution gates pass. [Data-only packaging](references/packaging-isolation.md) requires externally executed evidence bound to exact bytes; the packager must not execute target-owned validators.

## Output contract and stop conditions

Return `Planning context`, `Artifact decisions`, `Traceability`, `Risk and compatibility`, `Validation`, `Handoff or reconciliation`, and `Blockers`; include profile/stage/mode, identity, evidence/assumptions, paths changed/skipped, rationale, traceability, compatibility/migration/security/operations/rollback/privacy impacts, exact command outcomes, downstream handoff, and remaining work. Native publication must include verified `artifact_actions` and `artifact_actions_validation`; separate source changes from disposable projection refresh. Separate executed evidence from planned validation.

Stop before write/readiness when owner/root/identity is unresolved for mutation; canonical identity conflicts; evidence cannot support intent; another owner is required; a second source of truth or editable generated view would result; Magia evidence would be rewritten; runtime proof would be fabricated; protected fixtures/evaluators/reports/secrets would be touched; or required traceability, dependency, security, migration, compatibility, transaction, privacy, package, rollback, or distribution gates fail.
