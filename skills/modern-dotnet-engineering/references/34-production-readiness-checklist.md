# Production Readiness Checklist

## Evidence rule

Evaluate every required gate with one evidence state: `executed`, `observed`, `supplied`, `inferred`, `planned`, or `blocked`. For a positive production verdict, required gates need credible `executed` or `supplied` evidence appropriate to that gate. Static inspection alone does not prove runtime, deployment, capacity, security, or operational behavior.

## Verdict scale

- `approved`: all required gates have sufficient evidence, no unresolved blocking finding exists, and residual risk is bounded.
- `approved with reservations`: deployment gates are sufficiently evidenced, but non-blocking medium/low risks or bounded operational follow-ups remain.
- `blocked`: a required gate fails, required evidence is blocked, a critical finding remains unresolved, or a reachable high-severity risk lacks adequate mitigation.

Do not use `approved with reservations` as a substitute for missing evidence on a required gate.

## Required gates

### Platform/build/supply chain

- Supported .NET/runtime/SDK policy is known; production artifacts use an acceptable servicing level.
- SDK selection and package graph/lock state are reproducible enough for the repository's release policy.
- Restore/NuGet audit has a known outcome; transitive vulnerability findings are investigated or explicitly risk-owned.
- Build passes under the intended SDK with the repository's warning/analyzer policy.

### Test/contract evidence

- Unit/integration/functional tests cover critical paths appropriate to the change.
- Critical pipelines prove expected test discovery/count so a false-green zero-test run cannot pass unnoticed.
- Public API/message/storage contracts are versioned, migrated, or backward-compatible for the deployment strategy.
- OpenAPI/contract diff evidence exists when externally consumed HTTP contracts are material.

### Security/API boundaries

- Security review covers authentication, operation authorization, resource/object/property authorization, secrets, sensitive data, and logging.
- Externally reachable APIs have justified bounds for payload, pagination/query complexity, rate/concurrency, expensive operations, and timeouts.
- Negative cross-user/cross-tenant/resource-ownership tests exist for sensitive object access.

### Data/consistency

- Database migrations are reviewed for data loss, lock/deploy risk, rollback/forward recovery, compatibility, and execution ownership.
- Optimistic-concurrency conflicts have an explicit business resolution where stale writes matter.
- External calls have explicit timeout/retry behavior; retries do not amplify unsafe side effects.
- Idempotency exists for retryable critical operations/messages where duplicate effects are harmful.
- Durable message flows define duplicate, retry, poison/dead-letter, ordering, and recovery semantics.

### Operations/deployment

- Observability covers the signals needed to detect and diagnose important failures, with cardinality/privacy reviewed.
- Capacity/performance/reliability claims are supported by executed load/runtime evidence or credible supplied production telemetry.
- Health checks and graceful shutdown match the hosting/dependency model.
- Container/self-contained artifacts have runtime/base-image patch ownership and are rebuilt/redeployed for applicable servicing.
- Runbook and rollback/forward-recovery plan exist for important services or risky changes.

### Conditional gates

- Native AOT/trimming: intended publish completes with warnings fixed or explicitly reviewed, and the published artifact passes smoke/integration tests; framework/package compatibility is known.
- Aspire: solves a demonstrated orchestration/observability need and ServiceDefaults contains only operational cross-cutting concerns.
- AI/agent/MCP: executable tool/action boundaries enforce schema validation, authorization/tenant scope, least privilege, destructive-action control, and sensitive-data rules; model/config identity is captured for behavioral evaluation.

## Gate output

For each failed or unverified required gate, report:

`gate -> evidence state -> observed/supplied evidence -> impact -> required next check/fix`

Do not collapse several unknown gates into a generic confidence statement.
