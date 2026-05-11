# .NET 10 Performance

## Performance order

1. Fix algorithmic and database issues first.
2. Remove N+1 and excessive materialization.
3. Add pagination and batching.
4. Measure hot paths.
5. Apply .NET/runtime-specific optimizations.

## .NET 10-aware practices

- Use `Span<T>`/`ReadOnlySpan<T>` for parsing hot paths where it improves allocations and clarity.
- Prefer source-generated serializers/mappers where appropriate.
- Use high-performance logging (`LoggerMessage`) for very hot logs.
- Avoid reflection in request/item hot paths.
- Consider NativeAOT for CLIs/workers/services where startup and footprint matter.

## Do not

- Cache without invalidation.
- Optimize before measuring.
- Use low-level memory APIs in ordinary business code.
