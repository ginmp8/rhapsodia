# Resilience: Timeout, Retry, Circuit Breaker, and Rate Limit

## Rules

- Every external call needs a timeout.
- Retry only transient failures.
- Retried operations must be idempotent or protected by idempotency keys.
- Use jittered backoff for retries.
- Use circuit breakers to protect dependencies and callers.
- Use rate limits to protect public or abuse-prone endpoints.
- Do not retry validation errors, authorization failures, or deterministic business conflicts.

## Review checks

- Is there a deadline/timeout?
- Are retries bounded?
- Is the operation safe to retry?
- Are failures logged with correlation id and dependency name?
- Is there a fallback or clear failure response?
