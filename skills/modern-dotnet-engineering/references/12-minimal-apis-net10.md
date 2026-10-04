# Minimal APIs in .NET 10

## Default stance

Prefer Minimal APIs for new bounded HTTP surfaces when they keep routing and endpoint behavior clear. Use Controllers when MVC extensibility, OData, JsonPatch, advanced model binding/filters, or an established controller convention materially helps.

## Built-in validation

ASP.NET Core 10 provides built-in Minimal API validation. Register it with:

```csharp
builder.Services.AddValidation();
```

The validation pipeline can validate query, header, and request-body values using DataAnnotations/IValidatableObject and returns HTTP 400 by default on validation failure. Integrate error formatting with `IProblemDetailsService` when the application standardizes `ProblemDetails`.

### Source-generation boundary

`AddValidation` uses source generation and discovers validatable types in the assembly where `AddValidation` is called. If Minimal API endpoint types live in another assembly, register validation from that assembly as well. Missing generated metadata can result in automatic Minimal API validation simply not running, so multi-assembly layouts need focused tests.

Do not assume the built-in validation layer replaces domain/application invariants or authorization.

## Required patterns

- Keep `Program.cs` small.
- Organize endpoints by feature/module.
- Use `MapGroup` for prefix, tags, authorization, and common metadata.
- Use `TypedResults`/`Results<T...>` for explicit contracts where useful.
- Use `ProblemDetails` and one deliberate validation policy.
- Pass `CancellationToken` through to the application layer.
- Keep business rules and resource authorization outside endpoint glue.
- Do not inject `DbContext` directly into endpoint business logic when an application/domain boundary exists.

## Example

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddValidation();

var app = builder.Build();
app.MapOnboardingEndpoints();
app.Run();
```

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

## Validation

For multi-assembly endpoint designs, add a functional test that sends invalid input and proves the handler is not invoked. For public contracts, generate and diff OpenAPI 3.1 in CI.

Fresh source: https://learn.microsoft.com/aspnet/core/release-notes/aspnetcore-10.0
