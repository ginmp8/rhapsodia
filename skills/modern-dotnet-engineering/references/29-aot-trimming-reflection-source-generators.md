# Native AOT, Trimming, Reflection, and Source Generators

## Decision rule

Prefer compile-time/source generation over runtime reflection when it materially solves a measured startup/hot-path problem, improves trimming/Native AOT compatibility, or strengthens a contract. Do not replace simple bounded reflection merely because a generator exists.

## ASP.NET Core Native AOT gate

Check the current ASP.NET Core Native AOT compatibility matrix before committing to AOT. In the .NET 10 documentation baseline:

- Minimal APIs have partial support;
- MVC is not supported;
- OData is not supported;
- some other framework capabilities have partial/unsupported status.

Therefore, an MVC/OData workload must not be targeted for Native AOT without a deliberate architectural change supported by current documentation and tests.

## Rules

- Avoid reflection/dynamic code in AOT-sensitive code paths unless the API is annotated/generated appropriately and validated.
- Cache reflection metadata if reflection is unavoidable in a hot path, but first ask whether the hot-path reflection itself is necessary.
- Treat startup-time discovery, tests, tooling, and carefully bounded plugin models as reasonable reflection use cases.
- Be explicit about dynamic serialization, assembly scanning/loading, proxies, runtime code generation, and third-party library compatibility.
- Prefer source-generated `System.Text.Json` metadata when AOT/trimming requires it; do not force it into ordinary JIT applications without a need.

## AOT/trimming validation gate

Before claiming Native AOT/trimming compatibility:

1. publish with the intended AOT/trimming settings for the target RID(s);
2. review/fix AOT and trimming warnings; unresolved warnings require an explicit risk decision and targeted proof, not a blanket "works" claim;
3. run functional/integration smoke tests against the published artifact, not only a normal JIT build;
4. verify third-party package compatibility and dynamic behavior;
5. benchmark startup/memory/size only when those benefits justify the compatibility cost.

A publish that completes with material AOT/trimming warnings is not enough evidence for compatibility.

## Use reflection for

- bounded startup-time discovery;
- tests and architecture rules;
- tooling;
- plugin models whose dynamic behavior is a real requirement and is not AOT-constrained.

## Avoid reflection for

- per-request mapping;
- per-message serialization decisions;
- high-volume object construction;
- security-sensitive dynamic dispatch.

Fresh source: https://learn.microsoft.com/aspnet/core/fundamentals/native-aot
