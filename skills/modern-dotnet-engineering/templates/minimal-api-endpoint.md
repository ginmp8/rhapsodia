# Minimal API Endpoint Template

This default intentionally does not require a mediator package. If the repository already uses a mediator and the decision matrix supports it, adapt the dispatch boundary without changing the HTTP contract.

Register ASP.NET Core 10 built-in validation in the assembly that defines the Minimal API endpoint types:

```csharp
builder.Services.AddValidation();
```

```csharp
public static class FeatureEndpoints
{
    public static IEndpointRouteBuilder MapFeatureEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v1/features")
            .WithTags("Feature")
            .RequireAuthorization("FeatureAccess")
            .ProducesProblem(StatusCodes.Status500InternalServerError)
            .ProducesValidationProblem();

        group.MapPost("/", CreateAsync)
            .WithName("CreateFeature")
            .Produces<CreateFeatureResponse>(StatusCodes.Status201Created)
            .ProducesProblem(StatusCodes.Status409Conflict);

        return app;
    }

    private static async Task<Results<Created<CreateFeatureResponse>, ValidationProblem, ProblemHttpResult>> CreateAsync(
        CreateFeatureRequest request,
        CreateFeatureUseCase useCase,
        CancellationToken cancellationToken)
    {
        var result = await useCase.ExecuteAsync(request, cancellationToken);
        return result.ToHttpResult();
    }
}
```

Resource/tenant authorization belongs in an explicit application/policy boundary when access depends on the loaded object; `RequireAuthorization` alone is only the coarse endpoint gate.
