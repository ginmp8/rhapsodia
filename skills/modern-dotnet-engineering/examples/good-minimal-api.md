# Good Minimal API Example

```csharp
app.MapOnboardingEndpoints();

public static class OnboardingEndpoints
{
    public static IEndpointRouteBuilder MapOnboardingEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v1/onboardings")
            .WithTags("Onboarding")
            .RequireAuthorization("OnboardingAccess");

        group.MapPost("/", StartAsync).WithName("StartOnboarding");
        return app;
    }

    private static async Task<IResult> StartAsync(StartOnboardingRequest request, ISender sender, CancellationToken ct)
    {
        var result = await sender.Send(new StartOnboardingCommand(request.Document), ct);
        return result.ToHttpResult();
    }
}
```

Why good: endpoint adapts HTTP; application handles workflow; token is propagated.
