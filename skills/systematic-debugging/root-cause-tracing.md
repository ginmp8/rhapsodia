# Root-Cause Tracing

## At a Glance

- **Purpose:** Trace a bad value, state transition, side effect, or decision backward from where it manifests to the earliest evidenced causal trigger that the target can responsibly correct.
- **Load when:** The visible failure occurs deep in a call/data/event chain, the immediate failing line only consumes already-invalid state, or the origin of a value/action is unclear.
- **Decision impact:** Determines where the permanent correction belongs, what upstream evidence to capture, and when a symptom-level guard is only mitigation.

## Contents

- Backward tracing loop
- Instrumentation when the chain is hidden
- Side effects and event chains
- Choosing the correction point
- Defense after diagnosis

## Backward tracing loop

1. **Observe the manifestation.** Capture the exact failure, location, and relevant state.
2. **Find the immediate cause.** Identify the operation that directly produced the failure.
3. **Ask what supplied that state.** Trace caller, producer, event, configuration, data transformation, or prior write.
4. **Repeat backward.** At each step preserve concrete values/identities rather than replacing evidence with a story.
5. **Stop at the earliest evidenced trigger the system can own.** External factors may be outside the codebase; in that case identify the first boundary where the system could have detected/handled them correctly.

Example chain:

```text
invalid output
<- consumer received invalid value
<- producer emitted invalid value
<- transformation used stale configuration
<- deployment loaded the wrong config version
```

The consumer may need a guard, but the permanent correction belongs at the source or ownership boundary supported by evidence.

## Instrumentation when the chain is hidden

Add the least-invasive temporary evidence at the operation **before** the bad state is lost or transformed. Useful context can include call stack, causal/request identity, sanitized input identity, version/config identity, and timestamps/order.

Do not assume one logging API or shell exists. Use the target platform's normal diagnostic mechanism. Avoid secrets, arbitrary environment dumps, customer payloads, and instrumentation that materially changes timing without recording that confounder.

## Side effects and event chains

For queues/events/workflows, trace producer -> transport -> consumer -> state write -> downstream observer. Capture message/event identity, attempt number, schema/version, ordering, idempotency state, and relevant state transitions. For tests that pollute global/filesystem state, isolate which test/action first creates the state; use test selection/bisection appropriate to the project's runner.

## Choosing the correction point

Prefer the earliest point that:

- owns the violated invariant or transformation;
- has enough information to reject/prevent the invalid state;
- does not duplicate another layer's responsibility;
- can be verified with a focused regression test.

A downstream guard may still be justified as defense-in-depth or failure containment, but label it separately from the causal correction.

## Defense after diagnosis

After the origin is understood, load [`defense-in-depth.md`](defense-in-depth.md) to decide whether independent safeguards belong at trust boundaries, domain/invariant owners, dangerous side-effect boundaries, or operational safety controls.
