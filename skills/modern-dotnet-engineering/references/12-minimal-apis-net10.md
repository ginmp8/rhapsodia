# Minimal APIs in .NET 10

## Default stance

Prefer Minimal APIs for new HTTP APIs unless Controllers solve a concrete need better, such as OData, JsonPatch, advanced MVC model binding, or heavy filter/application-model customization.

## Required patterns

- Keep `Program.cs` small.
- Organize endpoints by feature/module.
- Use `MapGroup` for prefix, tags, authorization, and common metadata.
- Use `TypedResults`/`Results<T...>` for explicit contracts.
- Use `ProblemDetails` and validation integration.
- Pass `CancellationToken` through to the application layer.
- Do not inject `DbContext` directly into endpoint logic when business rules exist.

## Example

```csharp
public static class OnboardingEndpoints
{
    public static IEndpointRouteBuilder MapOnboardingEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v1/onboardings")
            .WithTags("Onboarding")
            .RequireAuthorization("OnboardingAccess")
            .ProducesProblem(StatusCodes.Status500InternalServerError)
            .ProducesValidationProblem();

        group.MapPost("/", StartAsync)
            .WithName("StartOnboarding")
            .Produces<StartOnboardingResponse>(StatusCodes.Status201Created)
            .ProducesProblem(StatusCodes.Status409Conflict);

        return app;
    }
}
```
