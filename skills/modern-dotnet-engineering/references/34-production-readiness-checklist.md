# Production Readiness Checklist

## Verdict scale

- approved: major gates have evidence.
- approved with reservations: non-blocking risks remain.
- blocked: material correctness, security, data, or operational gaps remain.

## Gates

- Build passes with warnings as errors.
- Unit/integration/functional tests cover critical paths.
- Security review covers auth, secrets, PII, and logs.
- Database migrations are reviewed and deployable.
- External calls have timeouts and retry policy where appropriate.
- Idempotency exists for retryable critical operations.
- Observability covers logs, traces, metrics, dashboards, alerts.
- Health checks and graceful shutdown are implemented.
- Runbook and rollback plan exist for important services.
- Contracts are versioned or backward-compatible.
