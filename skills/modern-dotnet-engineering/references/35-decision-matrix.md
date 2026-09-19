# Decision Matrix

## Universal decision procedure

Before adding a pattern, dependency, layer, cache, queue, repository, mediator, or framework feature, answer in order:

1. What concrete current problem or contract requires it?
2. What existing repository/runtime capability already addresses that problem?
3. What is the smallest option that solves the problem completely?
4. What new failure modes, dependencies, operational work, or compatibility commitments does it add?
5. How will the decision be validated and, if needed, rolled back?

If the only justification is future flexibility, architectural fashion, or easier mocking, prefer no new pattern.

Tie-breaker when multiple options remain valid: preserve correctness/security/compatibility, then existing contracts, then choose the smallest change with the simplest validation and rollback.

## Interface?

Use when there is a real boundary, variation, external dependency, or test isolation need that cannot be expressed cleanly without it. Do not create `IThing` for every `Thing`.

## DDD?

Use for rich domain rules and invariants where the model materially improves correctness and shared business language. Avoid for CRUD screens with no meaningful business behavior.

## CQRS?

Use when command/query separation improves clarity, independent scaling/performance, security boundaries, or materially different models. Avoid split models by habit.

## Mediator?

Use when decoupling API/worker dispatch from use cases or centralized pipeline behavior provides concrete value. Avoid hidden control flow, handler chains by habit, or introducing a package merely to call one application service.

## Repository?

Use for aggregate persistence boundaries or when isolating persistence semantics materially protects the application/domain. Avoid a generic repository over every query when EF already expresses the query well.

## Cache?

Use for expensive, frequently-read, tolerably stale data with clear ownership, invalidation, and failure behavior. Avoid for correctness-critical or authorization-sensitive state unless consistency semantics are explicit.

## Outbox?

Use when committed database state must reliably publish an external message and dual-write failure matters. Avoid for purely in-process notifications or when atomic publication is already provided by the platform.

## Worker?

Use for long-running, asynchronous, retryable, scheduled, or message-driven work. Avoid fire-and-forget inside HTTP requests.

## Minimal API or Controller?

Use Minimal API by default for new APIs when it keeps routing and endpoint behavior clear. Use Controllers when MVC extensibility, OData, JsonPatch, advanced filters/model binding, or an existing controller convention is materially valuable.

## Evidence requirement

For architecture/review output, identify the concrete evidence or constraint that selected the option. If evidence is missing, label the recommendation `inferred` and state what would change the decision.
