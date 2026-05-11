# Good Handler Example

```csharp
public sealed class ApproveOnboardingHandler(IOnboardingRepository repository, IUnitOfWork unitOfWork)
{
    public async Task<Result> Handle(ApproveOnboardingCommand command, CancellationToken cancellationToken)
    {
        var onboarding = await repository.GetByIdAsync(command.OnboardingId, cancellationToken);
        if (onboarding is null) return Result.NotFound();

        onboarding.Approve(command.ApprovedBy);
        await unitOfWork.SaveChangesAsync(cancellationToken);
        return Result.Success();
    }
}
```
