# Logging, Observability, and PII

## Logging rules

- Use structured logging.
- Never log full secrets, bearer tokens, cookies, JWTs, private keys, session IDs, full connection strings, unnecessary PII, or sensitive prompt/tool payloads.
- Include correlation/trace id, operation id, tenant/partner context, and domain identifiers only when useful and safe.
- Do not use logs as the only audit trail.

## Levels

| Level | Use |
|---|---|
| Debug | local diagnosis, disabled/limited in production by default |
| Information | business-significant flow events |
| Warning | abnormal but recoverable conditions |
| Error | unexpected failure requiring attention |
| Critical | service/system integrity risk |

## Metrics and tracing

Capture latency, throughput, errors, dependency outcomes, queue depth, retry/dead-letter counts, saturation, and critical business-process milestones. Use OpenTelemetry conventions where possible and correlate inbound HTTP, outbound dependencies, and messaging.

ASP.NET Core 10 adds useful built-in authentication, authorization, and Identity metrics. Use them when they answer an operational/security question; do not collect labels merely because they exist.

## Cardinality and privacy gate

Before adding a metric/tag/log dimension, ask:

- Can cardinality grow with user/resource/request identifiers?
- Can it contain secrets, PII, tenant-sensitive values, or attacker-controlled strings?
- Can the telemetry backend sustain the resulting series/storage cost?
- Is the dimension required for an alert/SLO/debugging decision?

Prefer bounded enums/categories and traces/logs for high-cardinality identifiers.

## Operational evidence rule

Static code inspection cannot prove behavior under real load. For production-readiness, latency/capacity/reliability claims need appropriate executed load/runtime evidence or credible supplied production telemetry. Separate those claims from code-quality observations.
