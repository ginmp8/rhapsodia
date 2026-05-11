# Logging, Observability, and PII

## Logging rules

- Use structured logging.
- Never log full secrets, bearer tokens, cookies, JWTs, private keys, session IDs, full connection strings, or unnecessary PII.
- Include correlation id, operation id, tenant/partner context, and domain identifiers when useful.
- Do not use logs as the only audit trail.

## Levels

| Level | Use |
|---|---|
| Debug | local diagnosis, disabled in production by default |
| Information | business-significant flow events |
| Warning | abnormal but recoverable conditions |
| Error | unexpected failure requiring attention |
| Critical | service/system integrity risk |

## Metrics and tracing

Capture latency, throughput, error counts, queue depth, retry counts, dead-letter counts, and business process milestones. Use OpenTelemetry conventions where possible.
