# Engineering Principles

## Purpose

Use this reference for all .NET engineering decisions. It sets the default bias: simple, explicit, observable, secure, and easy to change.

## Principles

1. Prefer clarity over cleverness.
2. Prefer business language over technical ceremony.
3. Prefer direct code until variation, testability, or external boundaries justify abstraction.
4. Prefer explicit behavior over framework magic.
5. Prefer measured performance work over speculative optimization.
6. Prefer secure defaults over optional hardening.
7. Prefer validation at boundaries plus invariants inside the domain.
8. Prefer small changes with clear validation over broad rewrites.

## Default decision rule

Ask: what concrete problem does this pattern solve here?

- If the answer is "future flexibility", do not add the pattern yet.
- If the answer is "this external dependency must be isolated", add a boundary.
- If the answer is "this invariant must never be violated", move behavior into the domain model.
- If the answer is "this operation must survive retry/replay", design for idempotency.

## Review checks

- Can a new developer find the rule of business behavior quickly?
- Can the operation be cancelled, logged, and tested?
- Can failure be diagnosed without exposing secrets or PII?
- Is the extra abstraction paying rent today?
