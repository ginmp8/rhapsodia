# Dataframes, Charts, and Editors

## Data display choices

Use `st.dataframe` when users need interactive exploration, sorting, scanning, or column resizing. Use `st.table` for small static output. Use `st.metric` for a few important numbers, not for dense tables.

## Data editor design

Use `st.data_editor` when editing is central to the app. Avoid using it as a casual display table because edited data introduces validation and save semantics.

Recommended editor pattern:

1. Keep immutable source data.
2. Add stable IDs.
3. Configure visible and editable columns.
4. Disable columns that should not change.
5. Validate edited values.
6. Compute and show a diff.
7. Persist through an explicit save action.

## Column configuration

Use column configuration to communicate type and constraints. Configure numbers, dates, links, images, checkboxes, selectboxes, progress, and chart columns deliberately. This reduces user mistakes and improves readability.

## Chart selection

- Line chart: trend over an ordered dimension.
- Bar chart: category comparison.
- Area chart: stacked or cumulative magnitude over time.
- Scatter chart: relationship between measures.
- Map: geospatial points with latitude/longitude.
- Altair/Vega-Lite: declarative statistical visualization and faceting.
- Plotly: interactive dashboards with hover, zoom, legends, and complex figures.
- PyDeck: geospatial layers and map-centric analysis.
- Matplotlib: static plots and library compatibility.

## Chart review checklist

- Does the chart answer one question?
- Are axis labels and units clear?
- Is the aggregation visible or explainable?
- Is the time zone clear for time-series data?
- Is the chart filtered by the same criteria as the table/metrics?
- Is there a fallback for empty data?
- Are large datasets sampled or aggregated responsibly?

## Data loading and transformation

Keep transformations pure and testable. Put I/O in cached functions. Keep chart-building functions separate from data-loading functions so chart tests can use small fixtures.

## Handling large datasets

- Push filtering and aggregation into the database when possible.
- Cache result sets with TTL appropriate to freshness needs.
- Avoid rendering huge raw tables by default.
- Provide search/filter controls and summary metrics first.
- Consider pagination, sampling, or grouped aggregates.

## Geospatial data

Check coordinate column names, numeric types, and coordinate validity. For maps, avoid rendering sensitive exact locations unless users are authorized and the business purpose is clear.
