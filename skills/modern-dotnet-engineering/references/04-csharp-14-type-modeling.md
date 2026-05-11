# C# 14 and Type Modeling

## Type choices

| Scenario | Prefer |
|---|---|
| EF/DDD entity with identity | `class` |
| aggregate root | `class` |
| request/response DTO | `record` |
| command/query | `record` |
| integration event | `record` |
| small immutable value | `readonly record struct` when appropriate |
| behavior with state changes | `class` |

## Rules

- Use `sealed` unless inheritance is deliberate.
- Keep nullable reference types enabled.
- Avoid `record` for EF entities because entity tracking relies on identity/reference semantics.
- Use domain methods instead of public setters for invariants.
- Use `field` backed properties when simple validation is clearer than manual backing fields.
- Use extension members only when they improve discoverability and domain readability.

## Examples

```csharp
public sealed record StartOnboardingCommand(string Document, string RequestedBy);

public sealed class Onboarding
{
    public Guid Id { get; private set; }
    public OnboardingStatus Status { get; private set; }

    public void Approve(string approvedBy)
    {
        if (Status != OnboardingStatus.Pending)
            throw new DomainException("Only pending onboardings can be approved.");

        Status = OnboardingStatus.Approved;
    }
}
```
