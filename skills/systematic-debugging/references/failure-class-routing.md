# Failure-Class Routing

## At a Glance

- **Purpose:** Route an observed failure to the diagnostic strategy that produces the most information with the least unnecessary experimentation.
- **Load when:** The failure class is unclear, multiple classes overlap, or a specialized branch is needed beyond the root router.
- **Decision impact:** Selects the first evidence source, reduction technique, and acceptance evidence; prevents treating every bug as the same linear workflow.

## Contents

- Regression
- Input or data dependent
- Nondeterministic or flaky
- Distributed or integration
- Performance
- Crash, hang, and resource failures
- Environment and configuration
- Mixed failures

## Regression

Establish one known-bad and at least one known-good state. Compare changes first; when revisions can be classified automatically, use binary search/bisection. Keep the oracle stable across revisions. Distinguish code, dependency, config, data/schema, and infrastructure changes.

## Input or data dependent

Minimize the failing input, request sequence, event stream, or dataset while preserving the same failure signature. Remove one dimension at a time or use systematic subset reduction when an automated failure oracle exists.

## Nondeterministic or flaky

Freeze all controllable inputs: seed, versions, environment, concurrency, time source when injectable, and external fixtures. Repeat without changing the candidate to estimate failure frequency. Inspect races, ordering, shared mutable state, retries, timeouts, clocks, and resource contention. Use record/replay, race/sanitizer tooling, or deterministic schedulers only when supported.

## Distributed or integration

Choose one failing execution and correlate it end-to-end. Inspect contract/version/config at boundaries, context propagation, retry/attempt numbers, timeouts, idempotency, state transitions, and partial failures. Compare sender and receiver views rather than assuming one side is authoritative.

## Performance

Define the degraded metric and representative workload. Freeze a known-good baseline. Identify the constrained resource before touching code: CPU, allocation/GC, memory retention, I/O, network, locks/contention, database/query, or external dependency. Profile the suspected bottleneck and compare equivalent runs.

## Crash, hang, and resource failures

- **Crash/exception:** capture complete error/stack and relevant state, then trace backward.
- **Hang/deadlock:** inspect tasks/threads, waits, locks, queues, and ownership; a larger timeout is not causal proof.
- **Memory/resource:** measure growth/pressure and ownership/retention; increasing limits may be mitigation, not correction.

## Environment and configuration

Fingerprint known-good and failing environments. Compare runtime/tool versions, architecture, OS/container, locale/timezone, feature flags, config, credentials/permissions, dependency resolution, network/proxy, and CI/local differences. Avoid dumping secret values; compare presence, identity, or hashes when sufficient.

## Mixed failures

A failure can cross classes, such as a deployment regression that exposes a race only under load. Start with the class that has the strongest comparator or oracle, then reclassify as evidence changes. Do not force one label when interaction is part of the causal model.
