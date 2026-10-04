# Transactions, Concurrency, and Consistency

## Decision points

Use explicit transaction boundaries when multiple database operations must commit atomically. Use optimistic concurrency for aggregate updates where stale writes matter. Use distributed coordination only when the failure model requires it.

## Rules

- Keep transactions short.
- Do not perform slow external HTTP calls inside a database transaction unless unavoidable and explicitly justified.
- Prefer idempotency and retry-safe design over large distributed transactions.
- Use concurrency tokens for updates that must detect lost updates.
- Treat a concurrency exception as a business conflict decision, not as an automatic retry signal.
- Use outbox when committed state and an external message must not diverge.
- Coordinate retries with transaction semantics: retrying a database operation or transaction can repeat non-database side effects unless those effects are outside the retry scope or idempotent.

## Conflict-resolution choices

| Conflict | Typical policy |
|---|---|
| stale user edit | return conflict/current version and require explicit resolution |
| commutative/mergeable update | reload and merge with domain rules |
| transient database failure | bounded retry only when the whole unit is safe to retry |
| duplicate command/message | idempotency/inbox key and prior-result replay where appropriate |

## Consistency models

| Requirement | Approach |
|---|---|
| same database atomicity | EF transaction/unit of work |
| external message after commit | outbox |
| external service side effect | idempotency key + bounded retry + audit |
| long-running business process | workflow/saga/process manager when real multi-step compensation/recovery is required |
