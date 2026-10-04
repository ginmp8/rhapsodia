# Messaging, Workers, Channels, and Background Services

## Worker rules

- Use `BackgroundService` or platform-native worker patterns for long-running asynchronous work.
- Create a DI scope per unit of work/message when scoped dependencies are required.
- Pass `CancellationToken` through all operations.
- Stop gracefully: stop accepting new work, then finish/cancel in-flight work predictably and visibly.
- Log message id, correlation id, attempt, and outcome without sensitive payload leakage.
- Make handlers idempotent when messages can be redelivered.

## In-process queues and backpressure

When producer and consumer rates can diverge, prefer a bounded `Channel<T>` (or an equivalent bounded primitive) over an unbounded in-memory queue. Define capacity and full-mode behavior deliberately:

- wait/backpressure;
- drop newest/oldest/write;
- reject/admission failure.

Choose based on data-loss tolerance and caller semantics. Unbounded queues convert overload into memory growth and latency rather than solving it.

Use an in-process channel only for work that may be lost with the process. Use durable messaging when restart/crash survival is a requirement.

## Messaging review

- Is ordering required, and at what key/scope?
- What delivery/duplication semantics exist?
- What is retry policy and total retry budget?
- What goes to dead letter/poison handling?
- Is the message contract versioned?
- Is there outbox/inbox/idempotency where consistency requires it?
- How are queue depth, lag, retry, dead-letter, and saturation monitored?
- What happens on graceful shutdown during in-flight processing?

## Validation

Exercise duplicate delivery, reordering where possible, poison messages, dependency failure, cancellation, shutdown, and queue saturation. Capacity tests should demonstrate the intended backpressure behavior.
