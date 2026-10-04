# HTTP Client and Resilience: Timeout, Retry, Circuit Breaker, Rate Limit

## HttpClient lifetime

Use one deliberate modern lifetime model:

- long-lived/static `HttpClient` with `SocketsHttpHandler.PooledConnectionLifetime` when direct lifetime ownership is simple; or
- short-lived clients created by `IHttpClientFactory`, which pools handlers and centralizes configuration/resilience.

Do not create/dispose a new client per request. Do not capture factory-created/typed clients in long-lived singletons unless their handler/DNS lifetime behavior is understood.

## Microsoft.Extensions.Http.Resilience

The standard resilience handler can combine rate limiting, total timeout, retry, circuit breaker, and per-attempt timeout. Treat defaults as a starting point, not proof they fit the operation.

Review the effective composed behavior: stacking handlers can multiply retry counts or time budgets unexpectedly.

## Retry-safety gate

Before enabling retry, answer:

1. Is the failure transient?
2. Is the operation semantically idempotent, or protected by an idempotency key/deduplication mechanism?
3. Can a timed-out attempt have succeeded remotely?
4. What is the maximum total attempts/end-to-end deadline after all composed policies?
5. What happens when retries are exhausted?

Never assume POST or another state-changing operation is retry-safe merely because the transport/library retries it.

## Rules

- Every external call needs an explicit deadline/timeout appropriate to the dependency/workload.
- Retry only transient failures with bounded attempts and jitter/backoff when useful.
- Use circuit breakers when repeated dependency failure would otherwise amplify load/latency.
- Use rate limiting/admission control for public or abuse-prone endpoints.
- Do not retry validation failures, authorization failures, deterministic business conflicts, or unsafe side effects.
- Hedging is specialized: use only when redundant execution is safe and tail-latency benefit is measured.

## Validation

- Fault-test timeouts, connection failures, 5xx, cancellation, retry exhaustion, and "remote succeeded but caller timed out" scenarios.
- Verify effective total timeout and attempt count, not isolated policy settings.
- Test critical state-changing dependency calls for duplicate-effect safety.

Fresh source: https://learn.microsoft.com/dotnet/fundamentals/networking/http/httpclient-guidelines
