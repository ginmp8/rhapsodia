# Transactions, Concurrency, and Consistency

## Decision points

Use explicit transaction boundaries when multiple database operations must commit atomically. Use optimistic concurrency for aggregate updates where stale writes matter.

## Rules

- Keep transactions short.
- Do not perform slow external HTTP calls inside a database transaction unless unavoidable.
- Prefer idempotency and retry-safe design over large distributed transactions.
- Use concurrency tokens for updates that must detect lost updates.
- Use outbox for external messages that must correspond to committed data.

## Consistency models

| Requirement | Approach |
|---|---|
| same database atomicity | EF transaction/unit of work |
| external message after commit | outbox |
| external service side effect | idempotency key + retry policy + audit |
| long-running business process | workflow/saga/process manager |
