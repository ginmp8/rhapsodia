# Async, Tasks, and Cancellation

## Rules

- Use async all the way through I/O paths.
- Do not use `.Result` or `.Wait()` in ASP.NET Core application code.
- Do not use `Task.Run` to wrap database, HTTP, Redis, or queue calls.
- Put `CancellationToken` as the last parameter.
- Pass the token to EF Core, HttpClient, Redis, queues, delays, and long loops.
- Do not run parallel operations on the same `DbContext`.
- Use `Task` by default; use `ValueTask` only when an API benefits measurably or avoids allocation on a frequent synchronous completion path.

## Example

```csharp
public async Task<CustomerDto?> GetAsync(Guid id, CancellationToken cancellationToken)
{
    return await db.Customers
        .AsNoTracking()
        .Where(x => x.Id == id)
        .Select(x => new CustomerDto(x.Id, x.Name))
        .FirstOrDefaultAsync(cancellationToken);
}
```

## Cancellation behavior

Do not log expected cancellation as an error. Treat `OperationCanceledException` as cooperative shutdown/request abort unless evidence says otherwise.
