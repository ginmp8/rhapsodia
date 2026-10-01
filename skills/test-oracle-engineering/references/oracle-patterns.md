# Oracle Patterns

Use these patterns as starting points, then bind them to repository/source evidence.

## API or service behavior

Prefer a request through the real public handler/service stack with realistic serialization and persistence boundaries. Assert observable response plus relevant durable side effect. Avoid mocking the exact component whose behavior is under test.

## Authorization and tenant/identity boundaries

Include at least one denied or cross-identity case. A positive same-user case alone cannot prove an authorization boundary.

## Events and messaging

Assert the input, emitted/consumed event shape, idempotency key or dedupe behavior when relevant, and resulting state. For retry claims, distinguish transient retry from duplicate side effects.

## Data and migrations

Capture before/after invariants. Test representative existing data plus null/default/edge values relevant to the migration. Destructive changes require explicit authority outside this skill.

## Concurrency, idempotency, and retry

Use controlled competing operations or repeated delivery. Observe stable final state and duplicate side effects. A sequential happy-path test is insufficient for a concurrency claim.

## CLI/process

Assert exit code, bounded stdout/stderr semantics, and resulting file/state changes. Do not treat human-readable prose as a stable machine contract unless the CLI declares it.

## UI behavior

Prefer action/state semantics through the application test surface. Visual equivalence is a separate perceptual concern; use `perceptual-validation` when appearance itself is part of acceptance.

## Security finding verification

A finding is not confirmed from plausible static reasoning alone when an executable public-stack oracle is feasible. Keep exploit/proof code bounded to the authorized test environment and do not convert proof work into production remediation.

## Existing test reuse

Reuse an existing focused test when it actually exercises the claim. Record why it is sufficient. Passing unrelated suites is supporting evidence, not the oracle.
