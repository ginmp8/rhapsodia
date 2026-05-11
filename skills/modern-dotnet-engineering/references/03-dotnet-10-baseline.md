# .NET 10 Baseline

## Policy

Assume .NET 10 as the baseline. Do not optimize for older versions unless requested.

## Defaults

```xml
<TargetFramework>net10.0</TargetFramework>
<Nullable>enable</Nullable>
<ImplicitUsings>enable</ImplicitUsings>
<TreatWarningsAsErrors>true</TreatWarningsAsErrors>
<LangVersion>latest</LangVersion>
```

Use central package management with `Directory.Packages.props` for repository consistency.

## Feature adoption rule

Use .NET 10 features when they improve one of these:

- clarity;
- correctness;
- security;
- performance;
- operational reliability;
- reduced boilerplate.

Do not use a new feature merely because it exists.

## Recommended defaults

- Minimal APIs for new HTTP APIs.
- EF Core 10 when EF is suitable.
- OpenTelemetry and health checks in service defaults.
- source generators over runtime reflection when available.
- modern CLI/tooling in CI rather than checked-in tool binaries.
