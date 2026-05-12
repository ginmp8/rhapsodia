# Architecture and State

## Mental model

A Streamlit app is a Python script that is executed top-to-bottom to render the current view. User interactions typically trigger another run. Good apps are written so reruns are cheap, deterministic, and easy to reason about.

Design implications:

- Top-level code should describe the view and orchestrate calls.
- Expensive or repeated work should be moved into cached functions.
- User-specific workflow progress belongs in session state.
- Durable records belong in a database, object store, file store, or external service.
- Widgets are declarative: the same widget with the same key represents the same UI state across reruns.

## Project sizes

### Single-file demo

Use a single app.py when:

- the app has one page;
- data loading is simple;
- there is little or no business logic;
- the goal is exploration or demonstration.

Keep sections in functions:

```python
import streamlit as st

st.set_page_config(page_title="Demo", layout="wide")


def render_filters():
    with st.sidebar:
        return st.selectbox("Segment", ["All", "A", "B"], key="segment")


def render_main(segment: str):
    st.title("Demo")
    st.write(f"Selected: {segment}")


segment = render_filters()
render_main(segment)
```

### Small production app

Use modules when the app has repeated data access, reusable charts, tests, or multiple pages.

```text
app.py
src/
  data.py        # queries, file parsing, cache wrappers
  state.py       # session-state initialization and transitions
  charts.py      # chart builders
  views.py       # reusable UI sections
  settings.py    # env/secrets/config reading
pages/
  01_overview.py
  02_details.py
```

### Larger app

Use a package layout when the app is part of a product or needs CI:

```text
streamlit_app/
  app.py
  pages/
  src/streamlit_app/
    __init__.py
    config.py
    state.py
    data/
    services/
    components/
    charts/
    validators/
  tests/
  .streamlit/config.toml
  requirements.txt
```

Do not introduce this structure for a tiny throwaway example.

## Session state

Use session state for per-user UI state and workflow progress. Initialize keys before widgets or callbacks rely on them.

```python
import streamlit as st

DEFAULT_STATE = {
    "step": "upload",
    "selected_id": None,
    "filters_applied": False,
}

for key, value in DEFAULT_STATE.items():
    st.session_state.setdefault(key, value)
```

Prefer a small helper when state grows:

```python
def init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("active_tab", "summary")
    st.session_state.setdefault("last_refresh", None)
```

Avoid storing:

- large dataframes that can be cached instead;
- database connections or clients that belong in `st.cache_resource`;
- secrets;
- raw uploaded files after parsing unless there is a clear privacy and memory reason;
- objects that cannot be serialized when your environment enforces serializable state.

## Widget keys

Use explicit keys when:

- a widget appears conditionally;
- a widget is moved between tabs/pages/containers;
- the value is read by callbacks;
- multiple widgets share a label;
- tests need stable selectors.

Bad:

```python
st.text_input("Name")
```

Better:

```python
name = st.text_input("Name", key="profile_name")
```

## Callbacks

Callbacks should be short state transitions. Avoid heavy work inside callbacks because the app will rerun anyway.

Good callback:

```python
def reset_filters() -> None:
    st.session_state.region = "All"
    st.session_state.status = []

st.button("Reset filters", on_click=reset_filters)
```

Risky callback:

```python
def run_query_in_callback():
    st.session_state.df = very_expensive_query()
```

Prefer making the callback update state, then let the main script call a cached function based on that state.

## Forms

Use forms to batch inputs that should not trigger intermediate reruns.

Use forms for:

- search/filter panels with several fields;
- update/create records;
- prompt configuration;
- slow queries that should run only after submit.

Pattern:

```python
with st.form("search_form"):
    query = st.text_input("Search", key="search_query")
    limit = st.number_input("Limit", min_value=1, max_value=500, value=50, key="search_limit")
    submitted = st.form_submit_button("Search")

if submitted:
    results = search(query=query, limit=limit)
    st.dataframe(results, use_container_width=True)
```

Do not put `st.button` inside a form when you need independent button behavior; use `st.form_submit_button`.

## Tabs, expanders, popovers, dialogs, and fragments

- Tabs organize related views. Do not use tabs to hide heavy work unless the app avoids computing hidden tab content.
- Expanders are good for optional detail, logs, advanced settings, or explanations.
- Popovers are useful for compact filter panels or secondary controls.
- Dialogs are good for focused interactions such as confirmation, editing one record, or previewing details.
- Fragments are useful when part of the app should rerun independently or at a controlled interval.

Keep advanced rerun features simple and documented. If a user is new to Streamlit, prefer ordinary forms and explicit state first.

## Multipage apps

Use multipage apps when the user has distinct tasks, not merely many charts.

Good pages:

- Overview
- Customer details
- Data quality
- Admin/settings

Poor pages:

- Chart 1
- Chart 2
- Chart 3

Share state through `st.session_state`, shared modules, and cached functions. Avoid hidden global mutable state.

## Navigation state

When a workflow spans pages:

- store current entity id in session state;
- validate that it exists before rendering a detail page;
- provide a fallback link or message when state is missing;
- do not assume the user reached the page through the intended button.

Example:

```python
customer_id = st.session_state.get("customer_id")
if not customer_id:
    st.warning("Select a customer from the overview page first.")
    st.stop()
```

## Anti-patterns

- Re-querying the database on every widget interaction without cache or forms.
- Using session state as a database.
- Mutating a cached dataframe in place and expecting isolation.
- Creating API clients at top level on every rerun.
- Using global lists/dicts to store per-user state.
- Building a large custom framework for a simple dashboard.
- Hiding real errors with broad `except Exception` and `st.warning`.
- Depending on a manual click order without validating state.

## Architecture review checklist

Ask these questions when reviewing an app:

1. What reruns after each interaction?
2. What work is expensive and should be cached?
3. Which data is shared across users and which is per user?
4. Are widget keys stable?
5. Are form submissions used for batch actions?
6. Are pages/components separated by user tasks?
7. Does the app fail safely when state is missing?
8. Is there a smoke test or AppTest for the main flow?
