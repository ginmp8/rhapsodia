# Condition-Based Waiting

## At a Glance

- **Purpose:** Replace guessed sleeps with waits on the actual observable condition when elapsed time is not itself the behavior under test.
- **Load when:** Tests or asynchronous code use fixed delays, fail intermittently under load/parallelism, or wait for events/state/files/counts.
- **Decision impact:** Determines whether to poll/subscribe for a condition, when a timeout remains necessary, and how to avoid turning a timing symptom into a larger sleep.

## Contents

- Core rule
- Safe wait contract
- Common patterns
- When fixed time is correct
- Failure diagnosis

## Core rule

Wait for the state/event you need, not an estimate of how long it should take.

```text
bad:  sleep(500ms) -> assert state
better: wait_until(state == ready, timeout=5s) -> assert state
```

A condition wait still needs a bounded timeout so failures terminate with useful diagnostics.

## Safe wait contract

A reusable wait should:

- read fresh state on each check or subscribe to the real event;
- have an explicit maximum duration;
- report what condition was awaited and the last observed state;
- use a polling interval appropriate to the system when event subscription is unavailable;
- respect cancellation where the runtime supports it;
- avoid busy loops.

Prefer existing framework/test-runner wait primitives before inventing a custom helper.

## Common patterns

| Need | Condition |
|---|---|
| async operation completes | terminal state/event observed |
| expected events arrive | count or matching event reached |
| resource appears/disappears | existence/visibility predicate |
| queue drains | depth reaches expected threshold |
| distributed result arrives | correlated result/state transition observed |

## When fixed time is correct

A fixed delay is justified when elapsed time is the behavior under test, such as debounce/throttle intervals, lease expiry, or scheduled retry timing. First establish the triggering condition, then wait for the documented timing window. Record why the duration derives from the contract rather than convenience.

## Failure diagnosis

If condition waiting still times out, treat the timeout as a symptom. Inspect why the state transition/event did not occur: missing signal, race, deadlock, failed producer, lost message, stale read, clock issue, or incorrect test oracle. Do not increase the timeout repeatedly without evidence that the correct behavior merely needs more bounded time.
