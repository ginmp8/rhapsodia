# Messaging, Workers, and Background Services

## Worker rules

- Use `BackgroundService` or platform-native worker patterns.
- Create a DI scope per unit of work/message.
- Pass `CancellationToken` through all operations.
- Stop gracefully and avoid abandoning in-flight work without visibility.
- Log message id, correlation id, attempt, and outcome.
- Make handlers idempotent.

## Messaging review

- Is ordering required?
- What is retry policy?
- What goes to dead letter?
- Is the message contract versioned?
- Is there an outbox/inbox where consistency requires it?
- How is poison-message handling monitored?
