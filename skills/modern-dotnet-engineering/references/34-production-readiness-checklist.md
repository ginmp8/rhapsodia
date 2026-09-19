# Production Readiness Checklist

## Evidence rule

Evaluate every required gate with one evidence state: `executed`, `observed`, `supplied`, `inferred`, `planned`, or `blocked`. For a positive production verdict, required gates need credible `executed` or `supplied` evidence appropriate to that gate. Static inspection alone does not prove runtime, deployment, capacity, or operational behavior.

## Verdict scale

- `approved`: all required gates have sufficient evidence, no unresolved blocking finding exists, and residual risk is bounded.
- `approved with reservations`: deployment gates are sufficiently evidenced, but non-blocking medium/low risks or operational follow-ups remain.
- `blocked`: a required gate fails, required evidence is blocked, a critical finding remains unresolved, or a reachable high-severity risk lacks adequate mitigation.

Do not use `approved with reservations` as a substitute for missing evidence on a required gate.

## Required gates

- Build passes with warnings as errors.
- Unit/integration/functional tests cover critical paths appropriate to the change.
- Security review covers authentication, authorization, secrets, sensitive data, and logging.
- Database migrations are reviewed for data loss, lock/deploy risk, rollback/forward recovery, and compatibility where applicable.
- External calls have explicit timeout and retry behavior where appropriate; retries do not amplify unsafe side effects.
- Idempotency exists for retryable critical operations where duplicate effects are harmful.
- Observability covers the signals needed to detect and diagnose important failures.
- Health checks and graceful shutdown match the hosting/dependency model.
- Runbook and rollback/forward-recovery plan exist for important services or risky changes.
- Public API/message/storage contracts are versioned, migrated, or backward-compatible for the deployment strategy.
- Dependency, secret, and vulnerability checks required by repository policy have known outcomes.

## Gate output

For each failed or unverified required gate, report:

`gate -> evidence state -> observed/supplied evidence -> impact -> required next check/fix`

Do not collapse several unknown gates into a generic confidence statement.
