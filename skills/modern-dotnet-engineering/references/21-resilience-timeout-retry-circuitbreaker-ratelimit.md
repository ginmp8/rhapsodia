# HTTP Client and Resilience: Timeout, Retry, Circuit Breaker, Rate Limit

## HttpClient lifetime

Use one deliberate modern lifetime model:

- long-lived/static `HttpClient` with `SocketsHttpHandler.PooledConnectionLifetime` when direct lifetime ownership is simple; or
- short-lived clients created by `IHttpClientFactory`, which pools handlers and centralizes configuration/resilience.

Do not create/dispose a new client per request. Do not capture factory-created/typed clients in long-lived singletons unless their handler/DNS lifetime behavior is understood.

## Microsoft.Extensions.Http.Resilience

The standard resilience handler can combine rate limiting, total timeout, retry, circuit breaker, and per-attempt timeout. Treat defaults as a starting point, not proof they fit the operation.

Review the effective composed behavior: stacking handlers can multiply retry counts or time budgets unexpectedly.

## Alternate-path and amplification gate

Do not treat `AddFallback`, failover routing, degraded data or hedging as a safe-by-default fix for an unavailable dependency. Before adding one, document:

- **Failure chain and load shift:** which callers switch, worst-case diverted QPS/concurrency, per-request downstream cost, cold-cache stampede, shared databases/connections/rate limits, common-mode faults and restoration oscillation.
- **Semantic floor:** what lower-quality results are explicitly permitted and which invariants are not (authorization, tenant isolation, transaction correctness, durable side effects, data freshness requirements). Reject, fail closed or return typed partial results when the alternative cannot meet mandatory semantics.
- **Cross-policy budget:** total elapsed deadline, actual attempt count across SDK/HTTP middleware/Polly/delegating handlers and services, hedged concurrency, per-attempt timeout and cancellation behavior. Do not layer independent retries blindly.
- **Exercise alternate path:** fault injection under sustained load, ambiguous timeout-after-success, two dependency failures, cache cold-start, circuit recovery/oscillation and rollback/compensation; verify actual failure isolation and observe latency, saturation, retries and customer-visible degradation.
- **Simpler options:** harden the primary, pre-position data, split resource pools, shed lower-priority load, fail fast or use a continuously exercised equivalent endpoint before creating a rare alternate execution path. A circuit breaker is a trade-off, not an automatic requirement.

**Microsoft.Extensions.Http.Resilience detail:** `AddStandardResilienceHandler()` includes retries for all HTTP methods by default. For state-changing or otherwise unsafe methods, use `options.Retry.DisableForUnsafeHttpMethods()` (or a deliberately restricted method list) unless a verified idempotency/reconciliation contract makes retries safe. Inspect effective composition against package/framework version instead of assuming library defaults are stable.

References:
- https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience
- https://aws.amazon.com/pt/builders-library/avoiding-fallback-in-distributed-systems/
- https://sre.google/sre-book/addressing-cascading-failures/
- https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker

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
