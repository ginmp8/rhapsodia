# Dependency Injection and Lifetimes

## Default lifetimes

| Service | Lifetime |
|---|---|
| `DbContext` | scoped |
| repository/unit of work | scoped |
| application handler | scoped or transient |
| stateless formatter/mapper | singleton if thread-safe |
| background worker | singleton hosted service with scoped services created per operation |

## Rules

- Use constructor injection.
- Avoid injecting `IServiceProvider` except in factories/composition roots.
- Do not let singleton services depend directly on scoped services.
- Do not call `BuildServiceProvider()` inside normal service registration.
- Register dependencies by layer: `AddApplication`, `AddInfrastructure`, `AddApi`.
- Use options validation for configuration-dependent services.

## Worker pattern

Hosted services should create scopes explicitly:

```csharp
await using var scope = serviceScopeFactory.CreateAsyncScope();
var handler = scope.ServiceProvider.GetRequiredService<IJobHandler>();
await handler.HandleAsync(cancellationToken);
```
