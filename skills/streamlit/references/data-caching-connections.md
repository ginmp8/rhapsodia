# Data, Caching, Connections, Uploads, and Downloads

## Cache decision tree

Use `st.cache_data` when the function returns data:

- pandas dataframes;
- query results;
- parsed uploaded files;
- transformed data;
- API response payloads;
- serialized report bytes;
- deterministic ML inference results that are safe to share for the same inputs.

Use `st.cache_resource` when the function returns a long-lived resource:

- database engine or connection factory;
- HTTP client or SDK client;
- loaded ML model;
- vector store or retriever object;
- tokenizer;
- configuration object that is expensive to construct.

Do not cache:

- raw credentials;
- authorization decisions without tenant/user isolation;
- private user upload bytes in shared cache unless keying and retention are explicit;
- mutable objects that will be modified in place by user interactions;
- non-deterministic functions unless the cache key includes freshness controls.

## Cache data pattern

```python
import pandas as pd
import streamlit as st

@st.cache_data(ttl="10m", show_spinner="Loading data...")
def load_orders(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df

orders = load_orders("orders.csv")
st.dataframe(orders, use_container_width=True)
```

## Cache resource pattern

```python
import os
import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource(show_spinner=False)
def get_engine():
    url = os.environ["DATABASE_URL"]
    return create_engine(url, pool_pre_ping=True)

engine = get_engine()
```

Resource cache objects are shared across sessions. Only use this for resources that are safe to share and do not embed a user-specific permission boundary.

## Hashing and ignored arguments

When a cached function accepts an unhashable object such as a connection, use an underscore-prefixed argument to exclude it from the cache key.

```python
@st.cache_data(ttl="5m")
def query_orders(_engine, customer_id: str) -> pd.DataFrame:
    return pd.read_sql("select * from orders where customer_id = %(id)s", _engine, params={"id": customer_id})
```

This means `_engine` changes will not invalidate the cache. Ensure the non-underscored arguments uniquely define the result and privacy boundary.

## Freshness controls

Use these controls when data can become stale:

- `ttl` for time-based invalidation;
- a user-visible refresh button that clears a cache or changes a cache key;
- version or date parameters in cached functions;
- `max_entries` for memory control;
- data-source last-modified time as part of the cache key when available.

Pattern:

```python
if st.button("Refresh data"):
    load_orders.clear()
    st.rerun()
```

## Multi-tenant and user-specific data

Shared caches can leak data if the cache key does not include the full data boundary.

Safe enough:

```python
@st.cache_data(ttl="2m")
def load_user_rows(user_id: str, tenant_id: str) -> pd.DataFrame:
    ...
```

Risky:

```python
@st.cache_data
def load_rows():
    # internally reads current user from a global auth object
    ...
```

Make user/tenant/filter arguments explicit.

## Database queries

Recommendations:

- Parameterize SQL; do not concatenate user input into SQL strings.
- Keep connection/client creation in `st.cache_resource`.
- Keep query results in `st.cache_data` when repeatable and safe.
- Add query limits for exploratory apps.
- Display query time and row count when useful.
- Handle empty results explicitly.
- Avoid running write operations from a dashboard unless auth, confirmation, audit, and rollback are designed.

Query function shape:

```python
@st.cache_data(ttl="5m", max_entries=100)
def search_customers(_engine, status: str, limit: int) -> pd.DataFrame:
    sql = """
    select id, name, status, created_at
    from customers
    where (%(status)s = 'All' or status = %(status)s)
    order by created_at desc
    limit %(limit)s
    """
    return pd.read_sql(sql, _engine, params={"status": status, "limit": limit})
```

## API calls

For external APIs:

- Put base URL, key, and timeout in config/secrets.
- Use retries cautiously; do not retry non-idempotent writes blindly.
- Cache GET responses when freshness allows.
- Surface partial failures clearly.
- Avoid logging request/response bodies that may contain private data.

## File upload handling

Before parsing uploaded files, decide:

- accepted extensions and MIME types;
- max size;
- parsing library;
- schema/column validation;
- whether contents are sensitive;
- whether contents may be cached;
- whether derived outputs should be downloadable.

Pattern:

```python
uploaded = st.file_uploader("Upload CSV", type=["csv"], key="orders_upload")
if uploaded is None:
    st.info("Upload a CSV file to continue.")
    st.stop()

if uploaded.size > 5 * 1024 * 1024:
    st.error("File is too large. Maximum size is 5 MB.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as exc:
    st.error(f"Could not parse CSV: {exc}")
    st.stop()

required = {"id", "created_at", "amount"}
missing = required - set(df.columns)
if missing:
    st.error(f"Missing required columns: {sorted(missing)}")
    st.stop()
```

## Download handling

Use `st.download_button` for files generated from sanitized output.

```python
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download CSV",
    data=csv_bytes,
    file_name="filtered_orders.csv",
    mime="text/csv",
)
```

For Excel or binary formats, generate bytes in memory and set the correct MIME type. Avoid writing temporary files unless necessary; when temporary files are needed, clean them up.

## Data editor persistence

`st.data_editor` returns edited data. Treat it as proposed changes until validated.

Checklist before saving edits:

- schema validation;
- type conversion;
- missing required fields;
- duplicate key detection;
- authorization check;
- confirmation step;
- audit log;
- optimistic concurrency if editing shared data.

Pattern:

```python
edited = st.data_editor(df, key="orders_editor", num_rows="dynamic")
if st.button("Validate changes"):
    errors = validate_orders(edited)
    if errors:
        st.error("Fix validation errors before saving.")
        st.write(errors)
    else:
        st.success("Changes are valid.")
```

## Performance checklist

- Cache data and resources separately.
- Do not parse the same upload repeatedly on every interaction.
- Use forms for expensive filters.
- Filter in the database when datasets are large.
- Downsample or aggregate before charting very large datasets.
- Avoid rendering huge dataframes by default.
- Use pagination, search, or row limits.
- Defer non-essential expensive sections behind buttons, tabs with explicit control, or expanders with warnings.
- Measure execution time before optimizing.

## Privacy checklist

- Does any cache key omit user/tenant identity?
- Are uploaded files cached or logged?
- Are secrets ever printed through `st.write`, `st.exception`, or logs?
- Does a downloadable file include hidden columns or raw private data?
- Does a dataframe reveal rows outside the user's allowed scope?
- Are API errors sanitized before display?
