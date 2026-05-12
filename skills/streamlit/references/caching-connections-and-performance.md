# Caching, Connections, and Performance

## Cache selection

Use `st.cache_data` for data values: query results, parsed files, transformed dataframes, serialized API responses, inference outputs that are safe to share across users. Cached data should be treated as immutable from the caller's perspective.

Use `st.cache_resource` for shared resources: database engines, API clients, model objects, vector-store clients, and expensive singleton setup. Resource objects can be mutable and shared, so they must be concurrency-safe or carefully used.

## Cache key design

Cache keys are derived from function code and hashable arguments. Exclude unhashable or non-key arguments by prefixing parameter names with `_`. Use explicit parameters for tenant, environment, user-safe scope, filters, and freshness boundaries.

## TTL and invalidation

Use TTL when data changes outside the app. Use manual clear functions for administrative refresh. Avoid infinite caching for operational data unless the data is truly static.

## Database patterns

```python
@st.cache_resource
def get_engine():
    return create_engine(st.secrets["database"]["url"])

@st.cache_data(ttl=300)
def load_orders(status: str):
    engine = get_engine()
    return pd.read_sql("select * from orders where status = %(status)s", engine, params={"status": status})
```

Prefer parameterized queries. Do not concatenate user input into SQL. Keep write operations out of cached functions.

## API client patterns

Cache the client as a resource. Cache idempotent API responses as data with TTL. Handle rate limits and show useful retry messages without leaking tokens or raw headers.

## Model and ML patterns

Load models with `st.cache_resource`. Cache preprocessing dictionaries or metadata separately. Avoid storing user-specific private data in shared resources.

## Performance diagnosis

1. Identify which interaction feels slow.
2. Add timing around data load, transformation, chart rendering, and model calls.
3. Cache the largest deterministic cost first.
4. Move controls into forms when changes trigger too many reloads.
5. Reduce dataframe/chart size before rendering.
6. Use fragments for independently refreshing areas.

## Concurrency and shared state

Multiple users can share cached resources. Avoid mutable global state unless it is protected and intentionally shared. For per-user state, use session state.

## Cache safety checklist

- Is the cached value safe to share across users?
- Does the cache key include tenant/user scope when needed?
- Is TTL aligned with data freshness expectations?
- Are secrets excluded from cache output and logs?
- Are writes excluded from cached functions?
- Is the resource thread-safe or used conservatively?
