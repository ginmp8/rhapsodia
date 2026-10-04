# Stress Harness

Use this reference to design reproducible validation for bugs, side effects, regressions, and security issues.

## Harness phases

1. **Baseline**: run the normal flow once with a unique correlation id and record expected events, state, side effects, logs, and metrics.
2. **Hypothesis selection**: choose one bounded risk at a time.
3. **Fault injection**: duplicate, reorder, delay, mutate, crash, timeout, throttle, or deny dependencies.
4. **Stabilization**: wait for terminal state or quiet window.
5. **Assertions**: validate invariants across database, broker, DLQ, logs, external mocks, and audit records.
6. **Regression gate**: rerun baseline and high-risk negative cases after fixes.

## Hypothesis stress loop

Use one bounded hypothesis per validation cycle when the user asks to prove, replay, fuzz, load, or harden a flow. Do not bundle unrelated risks into a single pass/fail result.

1. State the hypothesis as a falsifiable claim: trigger, invariant, expected failure, affected state or side effect, and evidence source.
2. Freeze the baseline inputs, correlation id strategy, mocks, clock behavior, broker settings, retry policy, and expected terminal state before injecting faults.
3. Run the smallest stress scenario that can disprove or confirm the hypothesis: duplicate, reorder, delay, crash point, dependency fault, tenant mismatch, poison message, or replay.
4. Stabilize on terminal state, queue/topic quiet window, retry exhaustion, or timeout. Mark timeout as incomplete evidence unless the timeout itself is the defect.
5. Decide the hypothesis: confirmed, rejected, needs verification, or unsafe to execute. Record observed evidence and residual gaps.
6. After a fix, rerun the baseline and the failing stress case as a regression gate before moving to the next hypothesis.

## Scenario catalog

- boundary values: null, empty, whitespace, max/min, huge payload, malformed schema;
- duplication: same event id, same business key, different event id same business intent;
- concurrency: many events for same resource, cross-resource load, partition hot key;
- ordering: B before A, stale A after C, terminal state followed by intermediate event;
- replay/redrive: old event, DLQ redrive, offset rewind, batch reprocess;
- crash points: before/after state write, before/after publish, before/after external call, before/after ack/commit;
- dependency failures: timeout, 429, 500, partial response, invalid response, slow database/cache/broker;
- security abuse: tenant crossing, actor spoofing, payload escalation, injection, oversized arrays, sensitive log inspection;
- loop detection: repeated event type per correlation id, hop limit breach, increasing retry without state progress;
- mutation/property testing: remove auth/idempotency checks, flip comparisons, verify tests fail.

## Evidence schema

For each scenario record:

- scenario id and hypothesis;
- initial state and input;
- correlation id/event ids;
- fault injected;
- expected terminal state;
- observed events and consumers;
- side effects and counts;
- DLQ/retry/lag metrics;
- security decisions;
- logs checked for sensitive data;
- pass/fail/needs verification.

## Acceptance gates

A critical flow gate passes only when:

- happy path still reaches expected terminal state;
- duplicate and replay do not duplicate critical side effects;
- stale/out-of-order events do not regress state;
- tenant/resource mismatch is denied;
- poison message reaches controlled failure without event storm;
- DLQ/logs do not reveal secrets or avoidable sensitive data;
- retry/backoff/ack behavior is intentional;
- every residual gap is documented.

## Reproducible fuzzing evidence

When fuzzing is applicable, do not record only that a fuzzer ran. Preserve enough identity to replay the failure and compare later runs:

- fuzz engine and version when material;
- fuzz target or entrypoint identity;
- seed corpus identity/hash and corpus size;
- dictionaries/custom mutators when used;
- sanitizer/instrumentation profile;
- random seed when exposed by the engine;
- run/budget limits such as executions or wall-clock ceiling;
- coverage evidence appropriate to the target;
- crash/timeout signature;
- minimal reproducer identity/hash when minimization is supported;
- regression corpus status after a confirmed fix.

A corpus can be regression evidence only when its identity is preserved. Coverage is evidence that the target reaches code/state, not proof that all relevant properties were asserted.

## Reproducible concurrency evidence

Load/concurrency volume can reveal races but usually cannot reproduce a specific scheduler decision. For race-sensitive hypotheses, prefer a bounded schedule or interleaving strategy when the runtime/harness supports it:

1. freeze initial state, inputs, clock, partitions/keys, worker count, retry configuration, and dependency behavior;
2. define the synchronization points or event-order decisions that matter;
3. explore a bounded set of interleavings, schedules, or controlled event orders rather than relying only on uncontrolled load;
4. when a failure appears, preserve the exact failing schedule/event-order trace plus random seed if one exists;
5. replay that schedule/trace before calling the defect reproducible;
6. after the fix, rerun the same failing schedule plus the normal baseline.

Do not claim deterministic concurrency proof from a one-off load test whose failing interleaving cannot be replayed. When schedule control is unavailable, label the evidence stochastic/observed and preserve the strongest available event trace.
