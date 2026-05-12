# API Decision Guide

This guide helps choose Streamlit APIs without loading full external documentation. Verify exact signatures against official docs when precision matters.

## Page and text

| Need | Prefer | Notes |
|---|---|---|
| Browser title, icon, layout | `st.set_page_config` | Put near the top of the app before UI output. |
| Main title | `st.title` | One primary title per page is usually enough. |
| Section titles | `st.header`, `st.subheader` | Use consistent hierarchy. |
| Flexible output | `st.write` | Good default; can hide type-specific intent. |
| Markdown content | `st.markdown` | Use for formatted text; avoid unsafe HTML unless justified. |
| Small helper text | `st.caption` | Use for notes, units, data refresh time. |
| Code blocks | `st.code` | Good for generated snippets or config. |
| Equations | `st.latex` | Useful for formulas. |
| Status callout | `st.info`, `st.success`, `st.warning`, `st.error` | Keep severity meaningful. |

## Layout

| Need | Prefer | Notes |
|---|---|---|
| Main sections side by side | `st.columns` | Keep responsive width in mind. |
| Optional details | `st.expander` | Good for logs or advanced details. |
| Task groups | `st.tabs` | Avoid doing expensive hidden-tab work when possible. |
| Persistent filters/settings | `st.sidebar` | Keep primary content in main area. |
| Compact secondary controls | `st.popover` | Avoid nesting and overusing. |
| Focused edit/confirmation | `st.dialog` | Keep dialog state explicit. |
| Isolated rerun region | `st.fragment` | Use when rerun cost or cadence matters. |

## Input widgets

| Need | Prefer | Notes |
|---|---|---|
| One-time click | `st.button` | Use callbacks for small state transitions. |
| Boolean toggle | `st.checkbox` or `st.toggle` | Choose based on UX style. |
| Single choice | `st.radio` or `st.selectbox` | Radio for few visible options; selectbox for more. |
| Multiple choices | `st.multiselect` | Consider default empty vs common selections. |
| Numeric range | `st.slider` | Good for exploratory filters. |
| Exact number | `st.number_input` | Good for precise values and validation. |
| Text | `st.text_input`, `st.text_area` | Text area for prompts, notes, SQL fragments. |
| Date/time | date/time widgets | Always consider timezone and date boundaries. |
| File input | `st.file_uploader` | Validate size, type, schema, and privacy. |
| Camera/image | media widgets | Consider browser permission and privacy. |

## Data display

| Need | Prefer | Notes |
|---|---|---|
| Interactive table | `st.dataframe` | Best general table default. |
| Static small table | `st.table` | For compact non-interactive display. |
| Editable grid | `st.data_editor` | Validate edited output before persistence. |
| Single metric | `st.metric` | Add context and date ranges. |
| JSON/debug output | st json | Avoid exposing secrets or private records. |
| Download data | `st.download_button` | Build sanitized bytes/string with clear file name. |

## Charts

| Need | Prefer | Notes |
|---|---|---|
| Quick line/area/bar | Streamlit built-ins | Good for simple exploration. |
| Polished 2D charts | Altair or Plotly | Choose based on interactivity and style needs. |
| Matplotlib output | st.pyplot(fig) | Use explicit figure object; avoid global figure. |
| Map points | `st.map` or pydeck | Validate lat/lon column names and privacy. |
| Complex interactive chart | Plotly, Altair, PyDeck | Keep dependencies explicit. |

## Media

| Need | Prefer | Notes |
|---|---|---|
| Image | `st.image` | Avoid embedding huge images. |
| Audio/video | `st.audio`, `st.video` | Be mindful of file size. |
| User-provided media | uploader + media display | Validate MIME and size. |

## Caching and state

| Need | Prefer | Notes |
|---|---|---|
| Cache dataframe/query result | `st.cache_data` | Returns copies; best for serializable data. |
| Cache client/model/engine | `st.cache_resource` | Shared singleton; must be thread-safe enough. |
| Per-user UI state | `st.session_state` | Initialize keys explicitly. |
| Query string state | `st.query_params` | Useful for shareable links. |

## Execution control

| Need | Prefer | Notes |
|---|---|---|
| Stop early | `st.stop` | Use after invalid state, missing auth, or missing upload. |
| Force rerun | `st.rerun` | Use sparingly; avoid loops. |
| Spinner | `st.spinner` | Wrap slow operation for feedback. |
| Progress | `st.progress` | Use for multi-step work with known progress. |
| Toast/temporary status | status APIs | Do not hide important errors. |

## Connections

Use `st.connection` when it fits the data source and deployment model. For custom clients, wrap client construction in `st.cache_resource`. Keep credentials in `st.secrets` or environment variables.

## Authentication

Use Streamlit's authentication APIs when they match the deployment target and identity provider. For enterprise deployments behind a proxy or platform auth layer, keep the trust boundary explicit: know whether the app receives a verified user identity or only untrusted headers.

## Version-sensitive APIs

Some APIs change over time. For exact signatures, supported parameters, deprecations, or new features, check official docs. When docs are not available, phrase answers as patterns and avoid claiming exact parameter support.

## Selection rules

1. Start with built-in Streamlit features before adding third-party components.
2. Add dependencies only when built-ins do not satisfy the UX or data requirements.
3. Prefer explicit figures/data over global implicit state.
4. Prefer clear validation over clever callbacks.
5. Prefer official APIs over injecting custom HTML/CSS/JavaScript.
