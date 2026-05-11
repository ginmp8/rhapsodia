# Modern .NET Anti-Patterns

## Block or challenge these patterns

- `.Result`/`.Wait()` in async server code.
- `async void` outside UI/event handler cases.
- singleton `DbContext` or parallel use of one context.
- service locator as ordinary design.
- interfaces for every class.
- `Manager`, `Helper`, `Utils` god objects.
- anemic domain model where business rules are scattered.
- mediator chains without meaningful decoupling.
- cache without TTL or invalidation.
- logs with secrets/PII.
- raw SQL with concatenated input.
- automatic production migrations without deployment control.
- public API returning EF entities.
- domain events used as reliable external messaging.
- feature flags without owner or cleanup date.
