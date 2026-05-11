# Decision Matrix

## Interface?

Use when there is a real boundary, variation, external dependency, or test isolation need. Do not create `IThing` for every `Thing`.

## DDD?

Use for rich domain rules and invariants. Avoid for CRUD screens with no business behavior.

## CQRS?

Use when command/query separation improves clarity, performance, security, or scaling. Avoid split models by habit.

## Mediator?

Use to decouple API/worker from use cases and centralize behaviors. Avoid chains and hidden control flow.

## Repository?

Use for aggregate persistence boundaries or to isolate EF from application. Avoid generic repository over every query when EF already expresses the query well.

## Cache?

Use for expensive, frequently-read, tolerably stale data with clear invalidation. Avoid for correctness-critical or authorization-sensitive state.

## Outbox?

Use when committed database state must reliably publish an external message. Avoid for purely in-process notifications.

## Worker?

Use for long-running, async, retryable, scheduled, or message-driven work. Avoid fire-and-forget inside HTTP requests.

## Minimal API or Controller?

Use Minimal API by default for new APIs. Use Controllers when MVC extensibility, OData, JsonPatch, or advanced filters/model binding are material.
