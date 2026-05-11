# Minimal API Endpoint Template

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
        ISender sender,
        CancellationToken cancellationToken)
    {
        var result = await sender.Send(new CreateFeatureCommand(request.Name), cancellationToken);
        return result.ToHttpResult();
    }
}
```
