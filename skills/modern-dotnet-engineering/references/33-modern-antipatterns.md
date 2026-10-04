# Modern .NET Anti-Patterns

## Block or challenge these patterns

- `.Result`/`.Wait()` in async server code.
- `async void` outside UI/event-handler cases.
- singleton `DbContext` or parallel use of one context.
- service locator as ordinary design.
- interfaces for every class.
- `Manager`, `Helper`, `Utils` god objects.
- anemic domain model where meaningful business rules are scattered.
- mediator chains without concrete decoupling value.
- cache without TTL/invalidation/consistency ownership.
- logs/traces/prompts containing secrets or unnecessary PII.
- raw SQL with concatenated input.
- automatic production migrations without deployment/privilege/concurrency control.
- global/named EF query filters treated as authorization.
- public API returning EF entities.
- unbounded list endpoints, uploads, queues, or channels.
- blind retries of POST/state-changing operations without idempotency semantics.
- stacking resilience handlers without calculating effective attempts/deadline.
- domain events treated as reliable external messaging.
- microservices/CQRS/event-driven decomposition by fashion rather than deployment/data/failure requirements.
- Span/source generation/Native AOT introduced without a measured compatibility/performance need.
- Native AOT compatibility claimed from a warning-producing publish or from a normal JIT test run only.
- Aspire ServiceDefaults used as a shared application/domain dumping ground.
- prompt instructions treated as authorization for AI/MCP tool execution.
- feature flags without owner or cleanup condition/date.
