# Domain Events, Integration Events, Outbox, and Idempotency

## Distinctions

| Concept | Use |
|---|---|
| domain event | in-process notification that something happened in the domain |
| integration event | message to another bounded context/system |
| outbox | reliable publication after DB commit |
| inbox/idempotency store | reliable duplicate handling for received messages |

## Rules

- Do not treat in-process domain events as reliable external messaging.
- Use outbox when losing an external message after a DB commit would create inconsistency.
- Make consumers idempotent.
- Include message id, correlation id, causation id, occurred-at, and schema version.
- Retry with limits; route poison messages to dead letter.

## API idempotency

For critical POST operations, use idempotency keys tied to actor + operation + payload fingerprint where appropriate.
