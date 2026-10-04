# EF Core Checklist

- [ ] `DbContext` is scoped/short-lived and not shared across threads or concurrent operations.
- [ ] Read-only queries use `AsNoTracking` and project only required columns where appropriate.
- [ ] `Include`/graph loading is intentional and bounded; N+1 risk is understood.
- [ ] Provider-specific behavior is tested against the real provider when important.
- [ ] Named/global query filters are not being used as the sole authorization boundary.
- [ ] Optimistic-concurrency conflicts have an explicit business resolution where stale writes matter.
- [ ] Retries cannot repeat external side effects accidentally.
- [ ] Migrations are reviewed for data loss, locks, rolling-deploy compatibility, and forward/rollback recovery.
- [ ] Migration execution ownership is explicit; startup `MigrateAsync` is not assumed safe by default.
- [ ] JSON/vector/provider-specific features have real-provider integration evidence.
