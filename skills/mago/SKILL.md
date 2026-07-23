---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction strategy, refactoring plans, architecture decisions, planned-decision records, execution handoff plans, tasks, validation plans, contract specs, migrations, observability, operations, security/risk notes, discovery, ordering, and define/refine workflows. do not use for execution work, delivery governance/status reporting, stakeholder communication, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Mago owns intended technical planning from Nomia intake and repository evidence. It never changes product code, executes tests or deployments, owns delivery governance, accepts business risk, or fabricates runtime proof.

## Distributed ecosystem routing

Use the [routing contract](references/ecosystem-routing-contract.md) and [lifecycle](references/ecosystem-lifecycle.md). For multi-intent work, perform only the current Mago planning/reconciliation phase, then emit the typed handoff. Never absorb Nomia governance or Magia execution. `scripts/route_ecosystem_request.py` is a read-only owner projection; `scripts/handoff_ledger.py` records transport state without domain authority.

## Authority and canonical state

- Nomia writes requester, owner, dates, `business_priority`, stakeholders, roadmap, governance status/decisions, and release communication.
- Mago writes requirements, design, decisions, tasks, validation plans, `technical_criticality`, `execution_sequence`, technical risk, and execution handoff.
- Magia writes implementation, tests, runtime validation, and execution evidence.
- Exchange only `nomia_to_mago`, `magia_to_mago`, `mago_to_magia`, and `mago_to_nomia` through the strict [ecosystem handoff contract](references/ecosystem-handoff-contract.md) and `scripts/ecosystem_handoff.py`.
- Reject mixed ecosystem versions before mutation, unsupported envelope schemas, malformed provenance/privacy metadata, legacy compatibility switches, and wrong-owner fields.
- A Mago planning boundary is an authoring boundary; execution-required tasks are valid planning outputs when bounded, assigned to Magia, and linked to validation. Mago never executes them.

Write only under a resolved `BOARD_ROOT` using [canonical paths](references/canonical-paths.md), [concurrent identity](references/concurrent-planning.md), and [shared ownership](references/shared-artifact-ownership.md). Registry/cycle/spec identity is authoritative; catalogs, queues, deltas, adapters, traceability, compass, waves, and reconciliation reports are reproducible non-authoritative projections. Legacy planning enters only through `adapt`; legacy execution evidence must first be normalized by Magia.

## Required inputs and evidence

Before writes resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, evidence source, profile, lifecycle stage, one internal mode, and payload. `order` may create a new `spec_id` atomically after deduplication; package-scoped modes require an existing registry-backed `spec_id`. Prefer current registry/package values, typed Nomia handoff, repository evidence, and validated prior planning. Preserve unknowns as assumptions/blockers; never invent repository, dependency, runtime, or validation truth. Use [evidence rules](references/evidence-contract.md).

## Public workflow

For first use or unclear entrypoints, load [getting started](references/getting-started.md).

```text
clarify -> define -> analyze -> handoff -> reconcile
```

Select the least costly safe profile in [profiles and lifecycle](references/profiles-and-lifecycle.md): `quick` for one bounded low-risk change, `standard` for normal work, and `governed` for regulatory, privacy/security, contract/schema, migration, irreversible data, operational, cross-service, or multi-repository impact. A user cannot suppress required escalation.

For `standard`/`governed`, apply [requirements and traceability](references/requirements-and-traceability.md), [clarification readiness](references/clarification-readiness.md), and [clarification prioritization](references/clarification-prioritization.md): stable `REQ`, `AC`, `DECISION`, `task`, and `VAL` identifiers; EARS/BCP 14/Gherkin only where meaningful; chain `REQ -> AC -> DECISION -> TASK -> VALIDATION`.

## Internal mode router

Select exactly one write mode per mutation step:

| Intent | Mode |
|---|---|
| repository discovery | [discovery](references/modes/discovery.md) |
| deduplicate/register/order specs | [order](references/modes/order.md) |
| legacy/drift normalization | [adapt](references/modes/adapt.md) |
| seed one registry-backed package | [prepare-define](references/modes/prepare-define.md) |
| full package | [define](references/modes/define.md) / [refine](references/modes/refine.md) |
| product-only | [define-product](references/modes/define-product.md) / [refine-product](references/modes/refine-product.md) |
| task-only | [define-tasks](references/modes/define-tasks.md) / [refine-tasks](references/modes/refine-tasks.md) |
| architecture/contracts/migration/ops/security | [technical-design](references/modes/technical-design.md) |
| behavior-preserving simplification | [complexity-reduction](references/modes/complexity-reduction.md) |
| planned ADR | [architecture decisions](references/architecture-decisions.md) |
| reshape task plan | [reshape-tasks](references/modes/reshape-tasks.md) |
| compare plan with Magia evidence | [reconcile](references/modes/reconcile.md) |

## Planning sequence

1. Route non-Mago work; resolve identity/registry; select profile, stage, and mode.
2. Load [common planning](references/common-planning.md), then only triggered references.
3. Select each artifact through the [decision matrix](references/artifact-decision-matrix.md); templates are structural inputs, not creation triggers.
4. Apply [technical standards](references/technical-artifact-standards.md), [ADR quality](references/adr-quality.md), and [security-risk v2](references/security-risk-contract.md) only when triggered.
5. For existing specs, produce a [change delta](references/change-delta.md). For external formats use [interoperability](references/interoperability-and-reconciliation.md) and the [adapter contract](references/adapter-development-contract.md); disclose losses and keep exports non-authoritative.
6. For multi-file writes, use the [transaction/resume contract](references/mutation-transaction-and-resume.md) and `scripts/mutation_transaction.py`; stage, validate, atomically promote, detect drift, and verify rollback.
7. Optional read-only views: [planning compass](references/planning-compass.md) via `scripts/render_planning_compass.py`, [execution waves](references/execution-wave-projection.md) via `scripts/render_execution_waves.py`, and [brownfield summary](references/brownfield-discovery-summary.md).
8. Handoff only clean, validated intent. Reconcile Magia evidence read-only and preserve provenance.

## Tools and validation

Use `scripts/create_planning_identity.py` for identity/registry creation and `scripts/write_artifact_scaffold.py` for supported scaffolds. Load branch guidance only when needed: [activation](references/activation-routing.md), [operating rules](references/operating-rules.md), [roadmap evidence](references/roadmap-evidence-input.md), [RFC quality](references/rfc-quality.md), [planning-execution handoff](references/planning-execution-handoff.md), [validation/packaging](references/validation-and-packaging.md), or [installation/release](references/installation-and-release.md).

Run the narrow applicable validators. Governed work requires current traceability/quality and security v2 where triggered; ecosystem releases require `scripts/validate_ecosystem_release.py` against explicit Mago, Magia, and Nomia roots. Package only after local package, contracts, provenance, routing, positive/negative lifecycle, recovery, and distribution gates pass.

## Output contract

Return concise Markdown with headings, in order: `Planning context`, `Artifact decisions`, `Traceability`, `Risk and compatibility`, `Validation`, `Handoff or reconciliation`, `Blockers`. Include selected profile/stage/mode, resolved identity, evidence/assumptions, exact paths created/updated/skipped, matrix rationale, traceability status, triggered compatibility/migration/security/operations/rollback impacts, commands with exact outcomes, downstream handoff, and remaining work. Separate executed evidence from planned validation.

## Stop conditions

Stop before writes/readiness when root or required identity is unresolved; registry/package truth conflicts; evidence cannot support canonical intent; another owner is required; quick escalation is rejected; a second source of truth or hand-edited generated view would result; Magia evidence would be rewritten; runtime proof would be fabricated; required traceability, dependency, security, migration, compatibility, transaction, package, or privacy gates fail; protected fixtures/evaluators/reports/secrets are targeted; or packaging validation fails.
