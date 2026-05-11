# .NET PR Checklist

- [ ] Async I/O uses `await` and propagates `CancellationToken`.
- [ ] No `.Result`, `.Wait()`, or fire-and-forget from HTTP request paths.
- [ ] `DbContext` is scoped and not used in parallel.
- [ ] Public APIs do not return EF entities.
- [ ] Logs are structured and do not expose secrets or unnecessary PII.
- [ ] Authorization is explicit for sensitive operations.
- [ ] External calls have timeout/retry policy where appropriate.
- [ ] Critical POST/message handlers are idempotent.
- [ ] Tests cover domain rules, persistence behavior, and API status codes as applicable.
- [ ] Build/analyzers/security scans pass or gaps are documented.
