# Data, Caching, and Connections

Use this reference for data loading, cache design, database connections, file processing, refresh behavior, and data freshness.

## Cache selection

Use data cache for serializable results: query outputs, dataframe transforms, parsed files, API responses, and deterministic computed values. Use resource cache for shared objects: database engines, API clients, model objects, vector stores, and expensive singletons.

## Cache controls

Add controls when freshness matters:

- time to live for periodically refreshed data;
- maximum entries for parameterized queries;
- user-visible refresh actions for manual invalidation;
- cache keys that include source, tenant, date range, or filter dimensions when needed.

## Privacy and tenant isolation

Treat shared caches as shared process-level state. Do not place user-specific authorization decisions, raw sensitive uploads, or tenant-private results in a shared cache unless the keying and isolation model are explicit.

## Connections

For database or API access:

- create the connection or client once through resource cache;
- query through data cache when results can be reused;
- pass filters as function arguments so cache keys reflect data boundaries;
- avoid constructing credentials in the UI path;
- load secrets from Streamlit secrets or environment variables.

## File uploads

For uploaded files:

- validate file type and size before parsing;
- parse to a safe in-memory object or temporary file only when needed;
- avoid logging raw contents;
- do not cache raw sensitive files globally;
- provide clear error messages for malformed input.

## Refresh patterns

Use periodic refresh only when the app really needs it. For operational dashboards, separate data collection from UI rendering when possible. For large data, prefer precomputed extracts, query limits, pagination, or lazy loading.
