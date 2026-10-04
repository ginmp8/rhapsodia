# EF Core 10 and Persistence

## Rules

- Treat `DbContext` as a short-lived unit of work; it is not thread-safe and must not be used concurrently.
- Use `AsNoTracking` for reads that do not need change tracking and project only the required columns into read DTOs.
- Avoid lazy loading in backend services unless the N+1/hidden-I/O trade-off is explicitly accepted.
- Use provider-real integration tests for relational behavior, migrations, JSON mapping, indexes, concurrency, and query translation.
- Keep migrations reviewed and deployment-controlled for critical systems.
- Never expose EF entities through public API contracts.

## EF Core 10 features to consider

- JSON complex-type mapping when document-shaped value data belongs to the aggregate and the real provider is validated.
- Vector search for AI/search use cases only when the selected provider supports the required semantics/performance.
- Named query filters when independent filters such as soft delete and tenant scoping need selective control.

## Named query filter boundary

Named/global query filters are convenience/data-scope mechanisms, not authorization. Disabling a filter must never be the operation that grants access. Entity/tenant ownership must still be enforced by explicit authorization/application rules.

## Migration strategy

Prefer migration execution as an explicit deployment step for important systems. Application-startup migration is not a neutral default because it can:

- require elevated schema privileges in the application identity;
- create races when multiple replicas start concurrently;
- couple availability/startup to migration duration/failure;
- make rollback/forward-fix coordination harder.

If startup migration is retained, document why the deployment topology and permissions make those risks acceptable.

## Concurrency

Use optimistic concurrency tokens where last-write-wins is unacceptable. Treat `DbUpdateConcurrencyException` as a business conflict that needs an explicit policy: reject/reload/merge/retry. Do not blindly retry the whole operation when external side effects could repeat.

## Query pattern

```csharp
return await db.Onboardings
    .AsNoTracking()
    .Where(x => x.Status == OnboardingStatus.Pending)
    .OrderByDescending(x => x.CreatedAt)
    .Skip((page - 1) * pageSize)
    .Take(pageSize)
    .Select(x => new OnboardingSummaryDto(x.Id, x.CompanyName, x.CreatedAt))
    .ToListAsync(cancellationToken);
```

## Validation gates

- Run migrations against the real provider and inspect generated SQL for risky changes.
- Test upgrade plus rollback/forward-fix on production-like data for material migrations.
- Exercise optimistic concurrency conflicts and confirm the intended business response.
- Use query-plan/EXPLAIN evidence before making performance claims.

## Avoid

- EF InMemory as proof of relational correctness.
- raw SQL with concatenated input.
- generic repositories that merely hide useful EF query semantics without protecting a real boundary.
