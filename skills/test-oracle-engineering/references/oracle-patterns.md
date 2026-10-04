# Oracle Patterns

Use these patterns as starting points, then bind them to repository/source evidence. Read [oracle-strategies.md](oracle-strategies.md) when direct expected output is unavailable or strategy selection is material.

## API or service behavior

Prefer a request through the real public handler/service stack with realistic serialization and persistence boundaries. Assert observable response plus relevant durable side effect. Avoid mocking the exact component whose behavior is under test.

## Authorization and tenant/identity boundaries

Include at least one denied or cross-identity case. A positive same-user case alone cannot prove an authorization boundary.

## Events and messaging

Assert input, emitted/consumed event shape, idempotency key/dedupe behavior when relevant, and resulting state. For retry claims, distinguish transient infrastructure failure from duplicate semantic side effects.

## Data and migrations

Capture before/after invariants. Test representative existing data plus relevant null/default/edge values. Destructive changes require explicit authority outside this skill.

## Concurrency, idempotency, and retry

Use controlled competing operations or repeated delivery. If the claim is about ordering/consistency rather than only final state, load [concurrency-distributed.md](concurrency-distributed.md) and capture/check the operation history. A sequential happy path or uncontrolled stress loop is insufficient for a concurrency claim.

## Property-based testing

Freeze the semantic property independently from generated examples. Record/replay the seed or minimized counterexample when material. Input generation increases exploration; it does not replace the oracle property.

## Metamorphic and differential testing

Freeze the metamorphic relation or differential references/decision rule before execution. Exclude undefined behavior explicitly. Treat disagreement as a signal requiring the declared rule, not automatic proof that one reference is correct.

## CLI/process

Assert exit code, bounded stdout/stderr semantics, and resulting file/state changes. Do not treat human-readable prose as a stable machine contract unless the CLI declares it.

## UI behavior

Prefer action/state semantics through the application test surface. Visual equivalence is a separate perceptual concern; use a perceptual validator when appearance itself is part of acceptance.

## Security finding verification

A finding is not confirmed from plausible static reasoning alone when an executable public-stack oracle is feasible. Keep proof code bounded to the authorized test environment and do not convert proof work into production remediation.

## Existing test reuse

Reuse an existing focused test only when it actually exercises the claim and its assertions can observe the relevant fault. Passing unrelated suites is supporting evidence, not the oracle. When false proof is costly, consider a targeted strength check rather than relying on coverage alone.
