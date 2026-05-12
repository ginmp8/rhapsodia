# UI and Interaction Patterns

Use this reference for Streamlit layout, charts, metrics, dataframes, editors, uploads, downloads, and user experience review.

## Layout defaults

- Use wide layout for dashboards with multiple charts or tables.
- Put global filters in the sidebar or a top-level form.
- Use columns for compact metrics or related controls.
- Use tabs for peer sections, not for hiding required steps.
- Use expanders for optional details, diagnostics, or advanced controls.

## Data display

Use interactive dataframes for exploration and static tables for small fixed outputs. Configure columns when names, formatting, links, images, progress bars, or editable fields need user-friendly presentation.

## Charts

Use built-in charts for simple line, area, bar, and map views. Use Plotly, Altair, PyDeck, or Matplotlib when the user needs advanced interaction, custom encodings, maps, statistical plots, or exact visual control. Keep chart functions testable by passing prepared dataframes and returning figures where practical.

## Data editing

When using editable data:

- validate edits before applying them to a database or downstream process;
- separate draft edits from committed state;
- show what changed before persistence;
- avoid writing to external systems on every rerun.

## Upload and download UX

For uploads, state accepted types, size constraints, and privacy implications. For downloads, generate explicit file names and formats. Cache generated exports only when data is not user-private or cache keys isolate the user and filters.

## Accessibility and clarity

Use clear labels, help text for non-obvious controls, units for numeric inputs, and status messages for long operations. Avoid relying only on color to communicate status.
