# Dataframes, Charts, and Editors

## Choose the native surface first

Use `st.dataframe` for interactive exploration, `st.table` for small static tables/key-value lists, and `st.data_editor` when editing is a first-class workflow. Prefer native Streamlit charts for common cases and declarative Vega/Altair for richer statistical charts. When the resolved version supports `st.echarts_chart`, use it for existing Apache ECharts/pyecharts definitions instead of adding a third-party component solely for ECharts.

## Accessible names

When supported, pass concise `alt=` text to charts, images, maps, media, iframes, PDFs, tables/dataframes/editors. The text should identify the content or takeaway, not repeat decorative surrounding copy. Verify the exact parameter against the installed version before adding it.

## Sensitive frontend payloads

Visual hiding is not data removal. Before rendering/exporting, remove columns/rows/records the current user is not authorized to receive. Do not send secrets or hidden tenant data to the browser and rely on column configuration to conceal it.

## Data editor workflow

1. Keep immutable source data and stable row IDs.
2. Configure visible/editable columns deliberately.
3. Validate edited values in Python; browser constraints are not security controls.
4. Compute/show the diff.
5. Persist only behind an explicit save action with authorization/idempotency as needed.

## Large datasets

Push filtering/aggregation to the source when possible, cache bounded result sets, and avoid rendering huge raw tables by default. Use pagination/lazy-source features only when supported by the resolved version and when they preserve correctness.

## Chart review

Confirm question, units, aggregation, time zone, filter consistency, empty states, accessible naming, and whether sampling/aggregation changes interpretation.
