# Risk and Validation Checklist

Use this checklist before finalizing a context map or implementation summary.

## Code risks

- Hidden callers or dynamic dispatch.
- Dependency injection registrations not updated.
- Public API or serialization contract changes.
- Generated code edited directly instead of generator source.
- Cross-language or cross-service clients not regenerated.
- Concurrency, retry, idempotency, timeout, or ordering assumptions changed.

## Data risks

- Destructive migration without compatibility path.
- Backfill, rollback, or dual-write requirement omitted.
- Index, constraint, or performance impact unreviewed.
- Timezone, nullability, precision, encoding, or collation changes.

## Configuration and deployment risks

- Feature flag missing or not documented.
- Environment-specific config not updated.
- CI, container, scheduler, or infrastructure references missed.
- Secrets or credentials exposed in examples, logs, or config.

## Observability risks

- Logs no longer identify the failing entity or correlation id.
- Metrics or traces missing for a new branch.
- Alert thresholds or dashboards not updated for changed behavior.

## Security and compliance risks

- Authorization, tenancy, or data-scope checks bypassed.
- Sensitive fields newly logged or returned.
- Input validation or output encoding weakened.
- Audit trail or regulatory reporting impact omitted.

## Validation evidence levels

- **Strong**: targeted tests passed and affected integration path was validated.
- **Moderate**: compile/type checks passed and tests cover adjacent behavior.
- **Weak**: only static reasoning or partial files available.
- **Blocked**: validation command or required environment is unavailable.
