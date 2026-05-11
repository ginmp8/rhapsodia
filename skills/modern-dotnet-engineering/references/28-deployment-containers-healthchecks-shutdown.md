# Deployment, Containers, Health Checks, and Graceful Shutdown

## Runtime requirements

- Liveness and readiness endpoints should have different meanings.
- Startup should fail fast for invalid required configuration.
- Graceful shutdown should stop accepting new work and finish/cancel in-flight work predictably.
- Containers should run as non-root where possible.
- Secrets should arrive via platform secret mechanisms.
- Migrations should be deployment-controlled for critical systems.

## Health checks

- Liveness: process is alive.
- Readiness: app can serve traffic and dependencies are available enough for the workload.
- Avoid exposing sensitive dependency details publicly.

## Deployment checklist

Check config, secrets, database migrations, health endpoints, logs, metrics, rollback, and operational runbook.
