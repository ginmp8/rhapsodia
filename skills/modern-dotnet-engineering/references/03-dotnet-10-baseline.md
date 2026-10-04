# .NET 10 Baseline, Lifecycle, and Servicing

## Policy

Assume stable .NET 10 as the production baseline. Do not optimize for older versions unless requested, and do not adopt preview/RC SDKs or runtimes implicitly merely because they are installed.

Support and patch status are freshness-sensitive. Verify the current Microsoft support policy when a production, upgrade, or security decision depends on it.

## Research snapshot

As of 2026-10-04, .NET 10 is the current LTS baseline and .NET 8/.NET 9 are scheduled to leave support on 2026-11-10. Treat this as dated evidence, not a timeless constant; reverify before using it as a release gate.

## Defaults

```xml
<TargetFramework>net10.0</TargetFramework>
<Nullable>enable</Nullable>
<ImplicitUsings>enable</ImplicitUsings>
<TreatWarningsAsErrors>true</TreatWarningsAsErrors>
<LangVersion>14.0</LangVersion>
```

Use central package management for multi-project repositories. When repeatable builds matter, pin a stable SDK policy with global.json and record the resolved SDK/runtime in CI evidence.

## Servicing rule

- Being on a supported major/minor release is insufficient if the deployed artifact embeds an obsolete servicing patch.
- Framework-dependent deployments receive runtime fixes through the hosting/runtime layer; self-contained and container deployments own rebuild/redeploy cadence for runtime fixes.
- Rebuild release artifacts after relevant runtime/base-image security servicing and verify the runtime in the final artifact, not only on the developer machine.

## Prerelease policy

Use preview/RC .NET only when the user/repository explicitly accepts prerelease support/compatibility risk and a concrete requirement justifies it. Keep stable production builds from opportunistically rolling onto prerelease SDKs.

## Reproducibility checks

For material build/runtime questions capture, as applicable:

- selected SDK policy from global.json;
- resolved output of `dotnet --info`;
- target frameworks and runtime identifiers;
- package graph/lock state;
- runtime version embedded in self-contained/container artifacts.

A package lock file does not by itself freeze SDK behavior; SDK/NuGet identity remains a build input.

## Feature adoption rule

Use .NET 10/C# 14 features when they improve clarity, correctness, security, performance, operational reliability, or boilerplate. Do not rewrite working code merely to consume new syntax.

## Recommended defaults

- Minimal APIs for bounded new HTTP surfaces when suitable.
- EF Core 10 when EF is suitable.
- OpenTelemetry and health checks in service defaults.
- Compile-time/source generation only when it solves a concrete AOT/trimming/startup/hot-path/contract problem.
- Modern CLI/tooling in CI rather than checked-in tool binaries.

## Fresh-source anchors

- Microsoft .NET support policy: https://dotnet.microsoft.com/platform/support/policy/dotnet-core
- global.json: https://learn.microsoft.com/dotnet/core/tools/global-json
