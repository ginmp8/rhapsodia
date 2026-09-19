# Risk and Validation Checklist

Use this checklist before finalizing a context map or implementation summary.

## Context-integrity risks

- Approved map is stale relative to revision/worktree or captured evidence hashes.
- Owner/source was confused with generated/derived output.
- Static search missed dynamic, reflection, convention, config-string, SQL-name, route, topic, or plugin consumers.
- Repository evidence conflicts with docs/tests/generated output and the conflict was silently resolved.
- Scope confidence is higher than evidence coverage supports.
- External consumers are assumed absent because they are not visible in the current repository.

## Code risks

- Hidden callers or dynamic dispatch.
- Dependency injection/runtime registrations not updated.
- Public API/serialization contract changes.
- Generated code edited instead of owning generator/source.
- Cross-language/cross-service clients not regenerated or versioned.
- Concurrency, retry, idempotency, timeout, locking, or ordering assumptions changed.

## Data risks

- Destructive migration without compatibility path.
- Backfill, rollback, dual-write, or dual-read requirement omitted.
- Index/constraint/performance impact unreviewed.
- Timezone, nullability, precision, encoding, or collation changes.

## Configuration and deployment risks

- Feature flag/default path missing.
- Environment-specific config not updated.
- CI/container/scheduler/infra references missed.
- Secrets or credentials exposed in examples, logs, or config.
- Rollout/rollback order incompatible with mixed versions.

## Observability risks

- Logs no longer identify the failing entity/correlation.
- Metrics/traces missing for a new behavior branch.
- Alerts/dashboards not updated when operational semantics change.

## Security and compliance risks

- Authorization, tenancy, data-scope, or audit checks bypassed.
- Sensitive fields newly logged/returned.
- Input validation/output encoding weakened.
- Regulatory/audit trail impact omitted.

## Validation evidence levels

- **Strong**: targeted tests passed and affected integration/runtime boundary was validated.
- **Moderate**: compile/type checks passed and tests cover adjacent behavior; some runtime path remains unexecuted.
- **Weak**: only static reasoning or partial repository evidence is available.
- **Blocked**: required validation or environment is unavailable.

Validation strength describes executed evidence, not plan quality.
