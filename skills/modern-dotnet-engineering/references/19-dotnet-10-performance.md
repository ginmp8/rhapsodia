# .NET 10 Performance

## Performance order

1. Fix algorithmic/database/network issues first.
2. Remove N+1, excessive materialization, and unnecessary round trips.
3. Add pagination/batching/admission control where needed.
4. Measure the real hot path and user-visible/system metric.
5. Apply runtime-specific optimizations only where evidence supports them.

## .NET 10-aware practices

- Upgrading the runtime/BCL can improve performance without application-code rewrites; measure before adding low-level complexity.
- Use `Span<T>`/`ReadOnlySpan<T>` for parsing hot paths only when it improves measured allocations/throughput without making APIs harder to use safely.
- Prefer source-generated serializers/mappers only when they solve a concrete startup/AOT/trimming/hot-path or contract need.
- Use high-performance logging (`LoggerMessage`) only for sufficiently hot paths.
- Avoid reflection in per-request/per-item hot paths; bounded startup/tooling reflection can be simpler and entirely acceptable.
- Consider Native AOT only when startup, memory, deployment size, or cold-start cost materially matters and the dependency graph is compatible.

## Measurement rules

- Quantified performance claims require executed/supplied benchmarks with scenario, environment, versions, repetitions/sample size, and measurement method.
- Prefer end-to-end latency, throughput, allocation, database/network cost, and capacity evidence over isolated microbenchmarks when the product concern is end-to-end.
- Re-run benchmarks on the published/deployed form when AOT, trimming, containers, tiered compilation, or deployment topology changes runtime behavior.

## Do not

- Cache without invalidation/consistency/failure semantics.
- Optimize before measuring.
- Use low-level memory APIs in ordinary business code without a demonstrated need.
- Treat source generation, Span, pooling, or Native AOT as universal best practices.
