# Good Minimal API Example

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
            .ProducesValidationProblem();

        group.MapPost("/", StartAsync).WithName("StartOnboarding");
        return app;
    }

    private static async Task<IResult> StartAsync(
        StartOnboardingRequest request,
        StartOnboardingUseCase useCase,
        CancellationToken cancellationToken)
    {
        var result = await useCase.ExecuteAsync(request, cancellationToken);
        return result.ToHttpResult();
    }
}
```

Why good: endpoint adapts HTTP; built-in request validation is registered; application code owns workflow and resource/business authorization; cancellation propagates. If endpoint types live in another assembly, register `AddValidation` in that assembly too and prove invalid requests are intercepted with a functional test.
