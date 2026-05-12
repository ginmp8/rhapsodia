# Recipes

Use these as starting patterns. Adapt them to the user's actual app, data, and deployment target.

## Data dashboard skeleton

```python
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")

@st.cache_data(ttl="10m")
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data.csv")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df

st.title("Dashboard")

df = load_data()

with st.sidebar:
    st.header("Filters")
    statuses = sorted(df["status"].dropna().unique())
    selected = st.multiselect("Status", statuses, default=statuses, key="status_filter")

filtered = df[df["status"].isin(selected)] if selected else df.iloc[0:0]

c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(filtered))
c2.metric("Total", f"{filtered['amount'].sum():,.0f}")
c3.metric("Average", f"{filtered['amount'].mean():,.2f}" if not filtered.empty else "-")

if filtered.empty:
    st.info("No rows match the selected filters.")
    st.stop()

st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button("Download filtered CSV", filtered.to_csv(index=False), "filtered.csv", "text/csv")
```

## Batched search form

```python
with st.form("search"):
    term = st.text_input("Search term", key="search_term")
    limit = st.number_input("Limit", min_value=1, max_value=500, value=50, key="search_limit")
    submitted = st.form_submit_button("Search")

if submitted:
    with st.spinner("Searching..."):
        results = search(term, int(limit))
    st.dataframe(results, use_container_width=True)
```

## Upload, validate, summarize

```python
import pandas as pd
import streamlit as st

uploaded = st.file_uploader("Upload orders CSV", type=["csv"], key="orders_file")
if uploaded is None:
    st.info("Upload a CSV to continue.")
    st.stop()

if uploaded.size > 10 * 1024 * 1024:
    st.error("Maximum file size is 10 MB.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as exc:
    st.error(f"Could not read CSV: {exc}")
    st.stop()

required = {"order_id", "created_at", "amount"}
missing = required - set(df.columns)
if missing:
    st.error(f"Missing required columns: {', '.join(sorted(missing))}")
    st.stop()

st.success(f"Loaded {len(df):,} rows.")
st.dataframe(df.head(100), use_container_width=True)
```

## Editable table with validation

```python
edited = st.data_editor(
    df,
    key="editor",
    hide_index=True,
    num_rows="dynamic",
    disabled=["id"],
)

if st.button("Validate", type="primary"):
    errors = []
    if edited["name"].isna().any():
        errors.append("Name is required.")
    if edited["amount"].lt(0).any():
        errors.append("Amount cannot be negative.")

    if errors:
        st.error("Validation failed.")
        st.write(errors)
    else:
        st.success("Changes are valid. Add a save step only after auth/audit is designed.")
```

## Cache a database client and query results

```python
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_engine():
    return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

@st.cache_data(ttl="5m")
def load_orders(_engine, status: str, limit: int):
    sql = """
    select id, status, amount, created_at
    from orders
    where (%(status)s = 'All' or status = %(status)s)
    order by created_at desc
    limit %(limit)s
    """
    return pd.read_sql(sql, _engine, params={"status": status, "limit": limit})

engine = get_engine()
orders = load_orders(engine, status, limit)
```

## Login guard shape

```python
import streamlit as st

if not getattr(st.user, "is_logged_in", False):
    st.title("Private app")
    if st.button("Log in"):
        st.login()
    st.stop()

st.write(f"Signed in as {st.user.email}")
```

Verify current auth API behavior against official docs for the Streamlit version used.

## LLM chat with reset

```python
import streamlit as st

st.session_state.setdefault("messages", [])

if st.sidebar.button("Reset conversation"):
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = generate_answer(prompt, st.session_state.messages)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
```

## Multipage shared state

```python
# src/state.py
import streamlit as st


def init_state():
    st.session_state.setdefault("selected_customer_id", None)
    st.session_state.setdefault("filters", {})
```

Call `init_state()` at the top of every page.

## Manual refresh button

```python
@st.cache_data(ttl="30m")
def load_data():
    ...

if st.button("Refresh data"):
    load_data.clear()
    st.rerun()

st.caption("Data refreshes automatically every 30 minutes or when manually refreshed.")
```

## Review checklist snippet

```markdown
## Findings
1. [high] Query runs on every widget change because filters are outside a form and query is uncached.
2. [medium] Uploaded file schema is not validated before charting.
3. [low] Metrics do not show data freshness.

## Fix sequence
1. Add `st.form` around filters.
2. Add `@st.cache_data(ttl="5m")` to query function with explicit user/tenant args.
3. Add upload schema validation.
4. Add `st.caption` with row count and refresh time.
```

## Docker-ready minimal app files

```text
app.py
requirements.txt
Dockerfile
.streamlit/config.toml
```

requirements.txt:

```text
streamlit
pandas
```

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

## When not to use a recipe

Do not use these recipes blindly when:

- the user has a specific existing app structure;
- production auth or tenant isolation is required;
- version-specific APIs must be exact;
- data is sensitive and upload/cache/logging rules are unclear;
- deployment platform has strict constraints.
