# Caching, Connections, and Performance

## Cache selection

Use `st.cache_data` for reusable serialized values: query results, parsed files, transformed dataframes, API payloads, and safe inference outputs. Use `st.cache_resource` for shared clients, engines, models, and expensive singleton resources. Do not wrap `st.connection()` in another resource cache; it already owns its connection lifecycle/cache semantics.

Treat cached data as immutable from the caller's perspective. Shared cached resources may be used concurrently by multiple sessions and must be thread-safe or deliberately serialized.

## Cache key and isolation

Cache keys derive from function code and arguments. Make tenant/user/environment/freshness scope explicit when it changes the returned data. Do not put private user or tenant data into a globally shared cache entry whose key omits the isolation dimension.

## Bound cache growth

Operational or parameterized caches should normally have a freshness or size policy (`ttl`, `max_entries`, or an equivalent project constraint). Unbounded changing caches can become a memory leak.

## Foreground vs background refresh

When the installed Streamlit version supports it, use background refresh only when serving a bounded stale value is acceptable. `refresh_mode="background"` trades freshness for latency and requires a TTL. Do not use it for data where stale reads violate correctness. Record the version dependency before introducing it.

## Async caching

When supported by the installed version, cached `async def` functions cache awaited results. Do not cache live async clients/connections tied to an event loop that may be closed on a later rerun. Cache loop-independent results or use a resource with a lifecycle compatible with the runtime.

## Database/API/model patterns

- Parameterize queries; never concatenate user input into SQL.
- Keep writes and other side effects out of cached functions.
- Cache idempotent API responses only when freshness and privacy allow it.
- Cache expensive model objects as resources only if their concurrency behavior is safe.

## Rerun reduction

Use the lowest-complexity control that fits the interaction:

1. ordinary rerun when work is cheap;
2. `st.form` to batch related inputs;
3. supported `on_change="ignore"`/equivalent no-rerun behavior for a control that should commit later;
4. `st.fragment` for an independently rerunning section;
5. parallel fragments only for independent slow work with thread-safe/shared-state discipline.

Cache expensive source data before cheap interactive filters instead of creating a cache entry for every UI combination. Render stable UI before slow work when possible.

## Performance evidence

1. Identify the slow interaction.
2. Measure load, transform, render, and external-call time separately.
3. Change one causal bottleneck or rerun boundary.
4. Re-measure with the same method and representative inputs.
5. Report trade-offs: freshness, memory, concurrency, or complexity.

Do not claim faster/cheaper without comparable evidence.
