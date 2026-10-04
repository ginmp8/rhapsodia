# Decision Matrix

## Universal decision procedure

Before adding a pattern, dependency, layer, cache, queue, repository, mediator, framework feature, distributed boundary, Aspire component, Native AOT requirement, or AI/MCP abstraction, answer in order:

1. What concrete current problem or contract requires it?
2. What existing repository/runtime capability already addresses that problem?
3. What is the smallest option that solves the problem completely?
4. What new failure modes, dependencies, operational work, security boundaries, or compatibility commitments does it add?
5. How will the decision be validated and, if needed, rolled back?

If the only justification is future flexibility, architectural fashion, easier mocking, or "modernity", prefer no new mechanism.

Tie-breaker when multiple options remain valid: preserve correctness/security/compatibility, then existing contracts, then choose the smallest change with the simplest validation, rollback, and operational burden.

## Architecture distribution gate

Default to a modular single deployable when independent deployment/data ownership/scaling/security isolation is not a demonstrated requirement.

Before microservices, separate read/write stores, or event-driven orchestration, explicitly price:

- data consistency and ownership;
- network/partial failure;
- message duplication/ordering/replay/idempotency;
- schema/version/deployment compatibility;
- observability and incident diagnosis;
- local/CI integration environments;
- capacity/on-call/deployment burden;
- workflow compensation/recovery.

## Interface?

Use when there is a real boundary, variation, external dependency, or test isolation need that cannot be expressed cleanly without it. Do not create `IThing` for every `Thing`.

## DDD?

Use for rich domain rules/invariants where the model materially improves correctness and shared business language. Avoid for CRUD screens with no meaningful business behavior.

## CQRS?

Use when command/query separation improves clarity, security, independent performance/scaling, or materially different models. Separate stores add synchronization/eventual-consistency cost and need a stronger justification than in-process command/query organization.

## Mediator?

Use when decoupling API/worker dispatch from use cases or centralized pipeline behavior provides concrete value. Avoid hidden control flow or adding a package merely to call one application service.

## Repository?

Use for aggregate persistence boundaries or when isolating persistence semantics materially protects the application/domain. Avoid a generic repository over every query when EF already expresses the query well.

## Cache?

Use for expensive, frequently-read, tolerably stale data with clear ownership, invalidation, authorization, and failure behavior. Avoid for correctness-critical or authorization-sensitive state unless consistency semantics are explicit.

## Outbox?

Use when committed database state must reliably publish an external message and dual-write failure matters. Avoid for purely in-process notifications or when atomic publication is already provided by the platform.

## Worker/channel/queue?

Use workers for long-running, asynchronous, retryable, scheduled, or message-driven work. Use bounded `Channel<T>` for in-process producer/consumer backpressure when loss on process failure is acceptable. Use durable messaging when survival/redelivery is required. Avoid fire-and-forget inside HTTP requests.

## Minimal API or Controller?

Use Minimal API by default for new bounded APIs when it keeps routing/endpoint behavior clear. Use Controllers when MVC extensibility, OData, JsonPatch, advanced filters/model binding, or an existing controller convention is materially valuable.

## Aspire?

Use when topology-as-code, local orchestration, service discovery, and telemetry defaults reduce real distributed-development friction. Do not use it as an application architecture framework or shared-domain container.

## Native AOT?

Use when startup, memory, size, or cold-start constraints are material and the ASP.NET/framework/package compatibility matrix supports the workload. Do not force AOT onto MVC/OData or reflection/dynamic-heavy systems without a supported migration path and published-artifact tests.

## AI / agents / MCP?

Use provider abstractions, agent frameworks, or MCP only when the application actually has model-driven behavior or needs interoperable tool/resource/prompt exposure. Keep deterministic business rules in code when they can be expressed directly. Never use prompt instructions as executable authorization.

## Evidence requirement

For architecture/review output, identify the concrete evidence or constraint that selected the option. If evidence is missing, label the recommendation `inferred` and state what would change the decision.
