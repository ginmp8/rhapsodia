---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction strategy, refactoring plans, architecture decisions, planned-decision records, execution handoff plans, tasks, validation plans, contract specs, migrations, observability, operations, security/risk notes, discovery, ordering, and define/refine workflows. do not use for execution work, delivery governance/status reporting, stakeholder communication, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Mago owns intended technical planning from Nomia intake and repository evidence. It never changes product code, runs tests/deployments, owns delivery governance, accepts business risk, or fabricates runtime proof.

## Distributed ecosystem routing

Use the [routing contract](references/ecosystem-routing-contract.md) and [lifecycle](references/ecosystem-lifecycle.md). Perform only the current Mago phase, preserve repeated phases, then hand off; never absorb Nomia or Magia authority. `scripts/route_ecosystem_request.py` is read-only; `scripts/handoff_ledger.py` stores transport state only.

## Authority and canonical state

- Nomia writes requester/owner/dates, `business_priority`, stakeholders, roadmap, governance decisions/status, closure, and release communication.
- Mago writes requirements, design, planned decisions/tasks/validation, `technical_criticality`, `execution_sequence`, technical risk, and execution handoff.
- Magia writes implementation, tests, runtime validation, execution decisions, and evidence.
- Use the strict [ecosystem handoff contract](references/ecosystem-handoff-contract.md) through `scripts/ecosystem_handoff.py`: consume `nomia_to_mago`/`magia_to_mago`; produce `mago_to_magia`/`mago_to_nomia`.
- Reject mixed ecosystem versions before mutation, unsupported envelope schemas, content/privacy-metadata contradictions, absent durable-artifact privacy lineage, legacy switches, and wrong-owner fields.
- A Mago planning boundary is an authoring boundary; execution-required tasks are valid planning outputs when bounded, assigned to Magia, and linked to validation. Mago never executes them.

Write only under a resolved `BOARD_ROOT` using [canonical paths](references/canonical-paths.md), [concurrent identity](references/concurrent-planning.md), and [shared ownership](references/shared-artifact-ownership.md). Registry/cycle/spec identity is authoritative; views are projections. Legacy planning enters only through `adapt`; legacy execution evidence must first be normalized by Magia.

## Required inputs and evidence

Before writes resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, evidence source, profile, lifecycle stage, one mode, and payload. `order` may atomically create a deduplicated `spec_id`; package modes require an existing registry-backed ID. Prefer current registry/package, typed handoff, repository, and validated planning evidence. Preserve unknowns; never invent technical, validation, or privacy truth. Apply [evidence rules](references/evidence-contract.md).

## Public workflow

For unclear entrypoints load [getting started](references/getting-started.md). Sequence: `clarify -> define -> analyze -> handoff -> reconcile`. Select [profile/lifecycle](references/profiles-and-lifecycle.md): `quick` only for bounded reversible low-risk work; `standard` normally; `governed` for regulatory, privacy/security, contract/schema, migration, irreversible data, operational, cross-service, or multi-repository impact. Standard/governed work applies [requirements/traceability](references/requirements-and-traceability.md), [clarification readiness](references/clarification-readiness.md), and [clarification prioritization](references/clarification-prioritization.md), preserving `REQ -> AC -> DECISION -> TASK -> VALIDATION`.

## Internal mode router

| Intent | Mode |
|---|---|
| discovery | [discovery](references/modes/discovery.md) |
| deduplicate/register/order | [order](references/modes/order.md) |
| legacy/drift normalization | [adapt](references/modes/adapt.md) |
| seed/full package | [prepare-define](references/modes/prepare-define.md), [define](references/modes/define.md), [refine](references/modes/refine.md) |
| product/task only | [define-product](references/modes/define-product.md), [refine-product](references/modes/refine-product.md), [define-tasks](references/modes/define-tasks.md), [refine-tasks](references/modes/refine-tasks.md) |
| architecture/contracts/migration/ops/security | [technical-design](references/modes/technical-design.md) |
| behavior-preserving simplification | [complexity-reduction](references/modes/complexity-reduction.md) |
| planned ADR | [architecture decisions](references/architecture-decisions.md) |
| reshape/reconcile | [reshape-tasks](references/modes/reshape-tasks.md), [reconcile](references/modes/reconcile.md) |

## Planning sequence

1. Route non-Mago work; resolve identity/registry, profile, stage, and exactly one mode.
2. Load [common planning](references/common-planning.md), then only triggered references.
3. Select artifacts with the [decision matrix](references/artifact-decision-matrix.md); templates do not trigger writes.
4. Apply [technical standards](references/technical-artifact-standards.md), [ADR quality](references/adr-quality.md), and [security-risk v2](references/security-risk-contract.md) only when triggered.
5. For existing specs produce a [change delta](references/change-delta.md). External formats use [interoperability](references/interoperability-and-reconciliation.md) and the [adapter contract](references/adapter-development-contract.md), disclose loss; remain non-authoritative.
6. Multi-file writes use the [transaction/resume contract](references/mutation-transaction-and-resume.md) and `scripts/mutation_transaction.py`: stage, validate, atomically promote, detect drift, and verify rollback.
7. Optional read-only outputs: [planning compass](references/planning-compass.md) via `scripts/render_planning_compass.py`, [execution waves](references/execution-wave-projection.md) via `scripts/render_execution_waves.py`, and [brownfield summary](references/brownfield-discovery-summary.md).
8. Handoff only validated intent; reconcile Magia evidence read-only with provenance.

## Tools and validation

Use `scripts/create_planning_identity.py` and `scripts/write_artifact_scaffold.py`. Load only needed guidance: [activation](references/activation-routing.md), [operating rules](references/operating-rules.md), [roadmap evidence](references/roadmap-evidence-input.md), [RFC quality](references/rfc-quality.md), [planning-execution handoff](references/planning-execution-handoff.md), [validation/packaging](references/validation-and-packaging.md), [installation/release](references/installation-and-release.md). Run narrow validators. Governed work requires current traceability/quality and security v2 when triggered; ecosystem release requires explicit Mago/Magia/Nomia roots. Package only after local, contract, provenance, routing, lifecycle, recovery, privacy, and distribution gates pass.

## Output contract

Return: `Planning context`, `Artifact decisions`, `Traceability`, `Risk and compatibility`, `Validation`, `Handoff or reconciliation`, `Blockers`. Include profile/stage/mode, identity, evidence/assumptions, paths changed/skipped, rationale, traceability, compatibility/migration/security/operations/rollback/privacy impacts, exact command outcomes, downstream handoff, and remaining work. Separate executed evidence from planned validation.

## Stop conditions

Stop before write/readiness when root/identity is unresolved; registry truth conflicts; evidence cannot support intent; another owner is required; required escalation is rejected; a second source of truth or editable generated view would result; Magia evidence would be rewritten; runtime proof would be fabricated; required traceability, dependency, security, migration, compatibility, transaction, privacy, package, or rollback gates fail; protected fixtures/evaluators/reports/secrets are targeted; or packaging fails.
