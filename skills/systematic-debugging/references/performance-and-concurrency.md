# Performance and Concurrency Debugging

## At a Glance

- **Purpose:** Diagnose performance regressions, races, deadlocks, timing failures, and resource pressure with baseline-comparable evidence.
- **Load when:** The symptom is slowness, throughput loss, high resource usage, flakiness, race/deadlock behavior, or timing-sensitive failure.
- **Decision impact:** Selects baseline/profile/stability evidence and prevents sleeps, larger limits, or retries from being mistaken for causal fixes.

## Contents

- Performance workflow
- Flakiness and races
- Deadlocks and hangs
- Resource pressure
- Timing and waiting

## Performance workflow

1. Define the degraded metric and acceptable comparator.
2. Freeze a representative workload and known-good baseline.
3. Identify the constrained resource or dependency before editing code.
4. Use counters/telemetry to localize, then profiling/tracing to identify the hotspot when available.
5. Form a causal hypothesis and change one relevant factor.
6. Repeat the same workload enough to distinguish signal from normal variance.

Do not claim improvement from incomparable workloads, warm/cold-state mismatch, changed data volume, or one noisy run.

## Flakiness and races

Repeat the unchanged candidate to characterize failure frequency. Freeze seeds/config/environment where possible. Look for shared mutable state, ordering, synchronization, async completion, retries, clocks, and resource contention. Use race detectors/sanitizers, deterministic schedulers, stress modes, or record/replay only when supported by the language/runtime.

A single pass after a change does not prove a flaky test is fixed.

## Deadlocks and hangs

Capture thread/task stacks, lock ownership, waits, queue depth, and dependency deadlines. Build a wait-for relationship when possible. Increasing a timeout may mitigate symptoms but does not explain the blocked dependency.

## Resource pressure

Measure allocations/retention, handles/descriptors, connection pools, queues, disk, network, or other constrained resources. Identify ownership/lifecycle before raising a limit. A higher limit is a resilience or capacity change unless evidence shows the limit itself was incorrectly configured.

## Timing and waiting

When code/tests wait for state transitions, prefer the actual state/event condition over guessed sleeps. Load [`../condition-based-waiting.md`](../condition-based-waiting.md) for the detailed pattern. Use fixed delays only when elapsed time is itself the behavior under test and document the timing contract.
