# EF Core Checklist

- [ ] `DbContext` is scoped and not shared across threads.
- [ ] Read-only queries use `AsNoTracking`.
- [ ] Queries project to DTOs where possible.
- [ ] `Include` is intentional and bounded.
- [ ] Migrations are reviewed.
- [ ] Relational behavior is tested with a real provider when important.
