# UI and Data Visualization

## UI principles

Streamlit apps are strongest when the page has a clear task. Design around what the user is trying to decide or do, not around how many widgets can fit on a page.

Good pages have:

- clear title and context;
- visible refresh/date range/data source;
- filters grouped away from results;
- primary metric or action near the top;
- chart/table choices matched to the decision;
- empty, loading, and error states;
- export or drill-down only when useful.

## Layout patterns

### Dashboard with filters

```python
st.title("Onboarding dashboard")

with st.sidebar:
    st.header("Filters")
    period = st.date_input("Period", key="period")
    status = st.multiselect("Status", ["Pending", "Approved", "Rejected"], key="status")
    apply_filters = st.button("Apply filters", type="primary")

if apply_filters:
    st.session_state.filters_applied = True
```

Use forms when filter changes should not run queries until submission.

### Summary metrics

Use metrics for a small set of important numbers.

```python
c1, c2, c3 = st.columns(3)
c1.metric("Opened accounts", 128, "+12%")
c2.metric("Median time", "2.4 days", "-0.3 days")
c3.metric("Pending review", 31, "+4")
```

Avoid displaying too many metrics without hierarchy.

### Master-detail

Use a table to select an entity and a detail area to show the selected record.

```python
event = st.dataframe(
    customers,
    use_container_width=True,
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun",
)
```

When using selection APIs, verify exact behavior with the Streamlit version in use.

## Tables

Use `st.dataframe` for interactive viewing. Add column formatting and hide columns when the user needs a readable business view, not a raw dump.

Recommended table practices:

- format currency, dates, percentages, and IDs;
- hide internal keys unless needed;
- show row count;
- offer download for filtered results;
- avoid rendering huge raw tables by default;
- include an empty-state message.

## Data editor

Use `st.data_editor` when the app is explicitly about editing data. Do not present it as a safe persistence mechanism without validation.

Common editor features:

- allowed column types;
- disabled columns for IDs or computed fields;
- dynamic rows only when create/delete is supported;
- validation before save;
- confirmation before writes;
- audit and rollback for production data.

## Charts

Choose charts by question:

| Question | Chart |
|---|---|
| Trend over time | line chart, area chart |
| Compare categories | bar chart |
| Show composition | stacked bar or limited pie/donut with caution |
| Distribution | histogram, box plot |
| Relationship | scatter plot |
| Geography | map only if location is central to decision |
| Funnel/process | bar/funnel-like sequence with conversion rates |
| Status over time | stacked area/bar or small multiples |

Do not use maps just because location fields exist. Use maps when spatial position changes the decision.

## Built-in charts vs external libraries

Use built-ins when:

- speed matters more than customization;
- the chart is simple;
- the app is a quick prototype.

Use Altair/Plotly/PyDeck when:

- tooltips, selections, facets, or complex encodings matter;
- you need polished layout;
- chart-specific config is important.

Use Matplotlib when:

- you already have Matplotlib code;
- output is static;
- scientific plotting is required.

When using Matplotlib, create explicit figures and pass them to Streamlit.

```python
fig, ax = plt.subplots()
ax.plot(df["date"], df["value"])
st.pyplot(fig)
```

## Empty, error, and loading states

Handle common states explicitly:

```python
if df.empty:
    st.info("No records match the selected filters.")
    st.stop()
```

Use `st.spinner` for slow work:

```python
with st.spinner("Running query..."):
    df = load_data(filters)
```

Display errors in user language, with technical detail only when helpful. Avoid dumping raw stack traces to untrusted users.

## Accessibility and readability

- Use descriptive widget labels.
- Avoid relying only on color to communicate status.
- Keep text contrast readable through theme choices.
- Use captions for units, data dates, and definitions.
- Keep column names human-readable.
- Prefer plain language for business users.
- Keep page hierarchy logical: title -> filters/context -> summary -> detail.

## UX review checklist

1. What is the primary user decision or action on this page?
2. Are filters understandable and grouped?
3. Does the page show data freshness?
4. Are table columns formatted for humans?
5. Is the chart type matched to the question?
6. Are empty/error/loading states handled?
7. Are downloads safe and named clearly?
8. Does the app work after reruns and navigation?
9. Is any advanced setting hidden behind an expander/popover?
10. Is performance acceptable for expected data size?
