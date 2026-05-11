# Caching

## Rule

Cache is an optimization, not the source of truth.

## Choose

| Scenario | Option |
|---|---|
| single instance, non-critical | `IMemoryCache` |
| multiple instances | distributed cache/Redis |
| L1+L2, stampede protection | `HybridCache` when available and suitable |
| authorization/PII-sensitive data | avoid or use very short TTL and strict isolation |

## Requirements

- Every cache key has namespace and versioning considerations.
- Every cached item has TTL.
- Invalidation strategy is documented.
- Stampede behavior is considered.
- Values are immutable or copied before mutation.
- Failures degrade safely.
