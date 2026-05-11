# EF Core 10 and Persistence

## Rules

- Treat `DbContext` as a short-lived unit of work.
- Do not share `DbContext` across threads.
- Use `AsNoTracking` for read-only queries.
- Project directly to DTOs for read models.
- Avoid lazy loading in backend services.
- Avoid `Include` unless the loaded graph is required.
- Use provider-real integration tests for relational behavior.
- Keep migrations reviewed and deployment-controlled.

## EF Core 10 features to consider

- JSON column mapping and complex types to JSON when data is semi-structured and owned by the aggregate.
- Vector search for AI/search use cases when the provider supports it.
- Named query filters when multiple global filters need selective disabling.
- Safer analyzer behavior around raw SQL patterns.

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

## Avoid

- EF InMemory as proof of relational correctness.
- raw SQL with concatenated input.
- exposing EF entities through public API contracts.
