# CQRS, Mediator, and DDD

## CQRS

Use commands for intent to change state and queries for data retrieval. Do not split models unless read/write requirements differ or the separation improves clarity.

## Mediator

Mediator is useful for decoupling endpoints/workers from use cases. It is not architecture by itself.

Rules:

- Handler should not return HTTP-specific types.
- Avoid chains of handlers calling mediator repeatedly without reason.
- Pipeline behaviors are good for validation, logging, metrics, and transactions.
- Business rules belong in application/domain, not pipeline behaviors.

## DDD

Use DDD where business rules, invariants, language, and lifecycle matter. Do not use rich aggregates for trivial CRUD.

- Entity: identity and lifecycle.
- Value object: equality by value.
- Aggregate root: protects invariants.
- Domain service: rule that does not naturally belong to one entity/value object.
