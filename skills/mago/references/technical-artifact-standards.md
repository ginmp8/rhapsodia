# Technical Artifact Standards

Load when MAGO defines/refines planned technical artifacts for a selected spec.

## Ownership and Evidence

Mago documents intended design; Magia documents implementation reality. MAGO artifacts must be grounded in repository evidence, Magnomo handoff evidence, user constraints, or explicit assumptions. Do not claim code changes, test runs, deployments, or runtime observations unless supplied evidence proves them.

## Canonical Technical Artifacts

- `technical-design.md`: trigger non-trivial design/architecture alignment; purpose intended components, boundaries, data flow, dependencies, constraints; template [assets/templates/technical-design.md.template](../assets/templates/technical-design.md.template).
- `complexity-reduction-plan.md`: trigger unnecessary abstractions, accidental complexity, excessive indirection, hard-to-change design; purpose evidence-backed simplification strategy, target seams, removal/merge candidates, phases, validation, rollback, Magia handoff; template [assets/templates/complexity-reduction-plan.md.template](../assets/templates/complexity-reduction-plan.md.template).
- `architecture-decisions.md` or `adrs/<adr_id>.md`: trigger material planned architecture decision; purpose ADR context/alternatives/consequences/validation expectations; template [assets/templates/adr.md.template](../assets/templates/adr.md.template).
- `implementation-plan.md`: trigger execution needs sequencing/strategy; purpose approach for Magia without writing code; template [assets/templates/implementation-plan.md.template](../assets/templates/implementation-plan.md.template).
- `tasks.md`: trigger work decomposition; purpose executable task structure for Magia; template [assets/templates/tasks.md.template](../assets/templates/tasks.md.template).
- `validation.md`: trigger proof plan; purpose checks Magia must run or evidence needed; template [assets/templates/validation.md.template](../assets/templates/validation.md.template).
- `contract-spec.md`: trigger intended/changed API, event, schema, interface, or file contract; purpose expected contract and compatibility; template [assets/templates/contract-spec.md.template](../assets/templates/contract-spec.md.template).
- `migration-strategy.md`: trigger data/schema/topic/cache/index migration; purpose order, compatibility, rollout, rollback; template [assets/templates/migration-strategy.md.template](../assets/templates/migration-strategy.md.template).
- `observability-design.md`: trigger production signals; purpose logs, metrics, traces, dashboards, alerts; template [assets/templates/observability-design.md.template](../assets/templates/observability-design.md.template).
- `operational-requirements.md`: trigger runbook/support/reprocessing needs; purpose expected operability requirements for Magia to implement/document; template [assets/templates/operational-requirements.md.template](../assets/templates/operational-requirements.md.template).
- `security-and-risk-considerations.md`: trigger security, PII, permissions, secrets, auth, compliance; purpose planned constraints/risks; template [assets/templates/security-and-risk-considerations.md.template](../assets/templates/security-and-risk-considerations.md.template).
- `open-questions.md`: trigger unresolved planning facts; purpose preserve questions/blockers, not invented facts; template [assets/templates/open-questions.md.template](../assets/templates/open-questions.md.template).

## Quality Bar

Every technical planning artifact includes: scope and selected spec; evidence or assumptions; intended design/decision/strategy; alternatives or explicit `none` where relevant; Magia validation expectations; risks/trade-offs; handoff instructions or blockers.

## ADR Criteria

Create a planned ADR for decisions affecting architecture, public contracts, persistence, distributed consistency, retries, idempotency, ordering, concurrency, security, migration, rollback, operability, observability, dependency selection, or future extension. Do not create ADRs for trivial task breakdown, local naming, or implementation details Magia can safely decide.

## Handoff to Magia

For implementation-bound technical plans, provide expected code areas when known; constraints/non-goals; validation commands/checks when known; migration/rollback expectations; contract compatibility; observability/operational requirements; risks Magia must revalidate.

## Boundary with Magia

MAGO may prescribe approach; it cannot claim implementation behavior unless Magia or repository evidence proves it. If implementation reality changes the design, consume Magia's technical-gap note or implementation ADR in a later refine run.

## Complexity-Reduction Criteria

Create `complexity-reduction-plan.md` when the primary change simplifies an existing system rather than adds behavior. Distinguish accidental from essential domain complexity and preserve externally observable behavior unless the spec explicitly requires behavior change.

Name the simplification hypothesis before task decomposition, such as "remove unused abstraction layer", "inline generic pipeline", "merge redundant service interfaces", "replace speculative configurability with explicit code path", or "split an over-broad module around stable seams". Each hypothesis needs evidence, expected benefit, blast radius, validation check, and rollback path. Do not plan broad rewrites because code looks complex; prefer small, reversible, behavior-preserving slices that Magia can execute and validate independently.
