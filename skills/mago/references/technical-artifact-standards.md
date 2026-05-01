# Technical Artifact Standards

Load this reference when MAGO defines or refines planned technical artifacts for a selected spec package.

## Ownership Model

Mago documents intended design. Magia documents implementation reality.

MAGO artifacts must be grounded in repository evidence, Magnomo handoff evidence, user-provided constraints, or explicit assumptions. They must not claim code was changed, tests were run, deployments happened, or runtime behavior was observed unless supplied evidence proves it.

## Canonical Planning Artifact Set

| Artifact | Trigger | Purpose | Template |
|---|---|---|---|
| `technical-design.md` | Non-trivial design or architecture alignment | Explain intended components, boundaries, data flow, dependencies, constraints | [assets/templates/technical-design.md.template](../assets/templates/technical-design.md.template) |
| `complexity-reduction-plan.md` | Application, module, or flow has unnecessary abstractions, accidental complexity, excessive indirection, or hard-to-change design | Define evidence-backed simplification strategy, target seams, removal/merge candidates, safe phases, validation, rollback, and Magia handoff | [assets/templates/complexity-reduction-plan.md.template](../assets/templates/complexity-reduction-plan.md.template) |
| `architecture-decisions.md` or `adrs/<adr_id>.md` | Material planned architecture decision | Record planned ADR with context, alternatives, consequences, and validation expectations | [assets/templates/adr.md.template](../assets/templates/adr.md.template) |
| `implementation-plan.md` | Execution needs sequencing or strategy | Explain how Magia should approach implementation without writing code | [assets/templates/implementation-plan.md.template](../assets/templates/implementation-plan.md.template) |
| `tasks.md` | Work needs decomposition | Create executable task structure for Magia | [assets/templates/tasks.md.template](../assets/templates/tasks.md.template) |
| `validation.md` | Work needs proof plan | Define checks Magia must run or evidence needed | [assets/templates/validation.md.template](../assets/templates/validation.md.template) |
| `contract-spec.md` | API/event/schema/interface/file contract is intended or changed | Define expected contract and compatibility | [assets/templates/contract-spec.md.template](../assets/templates/contract-spec.md.template) |
| `migration-strategy.md` | Data/schema/topic/cache/index migration is planned | Define order, compatibility, rollout, and rollback expectation | [assets/templates/migration-strategy.md.template](../assets/templates/migration-strategy.md.template) |
| `observability-design.md` | Production signals are needed | Define required logs, metrics, traces, dashboards, and alerts | [assets/templates/observability-design.md.template](../assets/templates/observability-design.md.template) |
| `operational-requirements.md` | Feature has runbook/support/reprocessing needs | Define expected operability requirements for Magia to implement/document | [assets/templates/operational-requirements.md.template](../assets/templates/operational-requirements.md.template) |
| `security-and-risk-considerations.md` | Security, PII, permissions, secrets, auth, or compliance matters | Define planned constraints and risks | [assets/templates/security-and-risk-considerations.md.template](../assets/templates/security-and-risk-considerations.md.template) |
| `open-questions.md` | Planning facts are unresolved | Preserve questions and blockers rather than inventing facts | [assets/templates/open-questions.md.template](../assets/templates/open-questions.md.template) |

## Required Quality Bar

Every technical planning artifact must include:

- scope and selected spec;
- evidence or assumptions;
- intended design/decision/strategy;
- alternatives or explicit `none` when relevant;
- validation expectations for Magia;
- risks and trade-offs;
- handoff instructions or blockers.

## ADR Criteria

Create a planned ADR when the decision affects one or more of:

- architecture, public contracts, persistence, distributed consistency, retries, idempotency, ordering, concurrency, security, migration, rollback, operability, observability, dependency selection, or future extension.

Do not create a planned ADR for trivial task breakdown, local naming, or implementation details Magia can safely decide during execution.

## Handoff to Magia

For every technical plan that expects implementation, provide enough information for Magia to avoid guessing:

- expected code areas when known;
- constraints and non-goals;
- validation commands or checks when known;
- migration and rollback expectations;
- contract compatibility requirements;
- observability and operational requirements;
- risks that must be revalidated during implementation.

## Boundary with Magia

MAGO can say how implementation should be approached. It cannot say how implementation actually behaved unless Magia or repository evidence proves it. If implementation reality changes the design, consume Magia's technical-gap note or implementation ADR in a later refine run.



## Complexity-Reduction Planning Criteria

Create a `complexity-reduction-plan.md` when the requested change is primarily about simplifying an existing system rather than adding behavior. The plan must distinguish accidental complexity from essential domain complexity and must preserve externally observable behavior unless the selected spec explicitly requires behavior change.

Complexity-reduction planning must name the simplification hypothesis before task decomposition, for example: "remove unused abstraction layer", "inline generic pipeline", "merge redundant service interfaces", "replace speculative configurability with explicit code path", or "split an over-broad module around stable seams". Each hypothesis must include evidence, expected benefit, blast radius, validation check, and rollback path.

Do not plan a broad rewrite merely because code looks complex. Prefer small, reversible, behavior-preserving slices that Magia can execute and validate independently.
