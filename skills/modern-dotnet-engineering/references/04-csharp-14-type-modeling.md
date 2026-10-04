# C# 14 and Type Modeling

## Type choices

| Scenario | Prefer |
|---|---|
| EF/DDD entity with identity | `class` |
| aggregate root | `class` |
| request/response DTO | `record` when value semantics fit |
| command/query | `record` when value semantics fit |
| integration event | `record` when immutable contract semantics fit |
| small immutable value | `readonly record struct` when copying/value semantics are appropriate |
| behavior with state changes | `class` |

## C# 14 adoption table

| Feature family | Default stance | Reason |
|---|---|---|
| `field`-backed properties, null-conditional assignment, cleaner lambda modifiers | use when clearer | reduces ceremony without changing architecture |
| extension members | conditional | useful for cohesive extensions; harmful as an ownership dumping ground |
| partial constructors/events and other source-generation-oriented features | specialized | primarily valuable for generators/framework tooling |
| Span/ref-like APIs, manual pooling, low-level memory techniques | measured hot paths only | increases lifetime/API complexity and should follow profiling |
| user-defined compound assignment or advanced operator features | domain/library-specific | use only when semantics remain obvious |

## Rules

- Keep nullable reference types enabled.
- Use `sealed` unless inheritance is deliberate.
- Avoid `record` for EF entities when value equality would conflict with identity/reference semantics.
- Use domain methods instead of public setters for invariants.
- Use `field`-backed properties when simple local validation is clearer than a manual backing field.
- Use extension members only when they improve discoverability and preserve clear ownership.
- Prefer runtime/language upgrades over hand-written micro-optimizations when the runtime already provides the gain.
- Do not imply that Span usage or source generation is automatically superior for ordinary business code.

## Validation

- Compile/analyze under the repository SDK and explicit C# language version.
- Require benchmarks for quantified performance claims caused by application-code changes.
- Review compatibility for public library API changes even when source syntax looks benign.

## Example

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
