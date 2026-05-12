# Streamlit API Catalog

This catalog is original guidance for deciding which Streamlit feature family to use. It is not a replacement for official API documentation. Verify exact signatures, new parameters, and deprecations against official docs when precision matters.

## Configuration

### `st.set_page_config`

Use for page title, icon, layout, sidebar state, and menu links. Put it near the top of the entrypoint. In multipage apps, keep page config intentional and avoid conflicting per-page assumptions.

### `.streamlit/config.toml`

Use for project runtime and theme defaults. Keep credentials out of this file. Prefer local project config for repository-specific behavior and global config only for developer preference.

### `st.secrets`

Use for secrets supplied by Streamlit deployment or local secrets files. Never print it. For local examples, provide `secrets.toml.example` with placeholders only.

## Text and display

### `st.write`

Use for quick display of strings, dataframes, objects, charts, and markdown-like values. For production UI, prefer explicit APIs when intent matters.

### `st.markdown`

Use for formatted content. Avoid `unsafe_allow_html=True` unless the risk and deployment context are understood. Prefer native components before custom HTML.

### `st.title`, `st.header`, `st.subheader`

Use to create a readable hierarchy. Do not use headings as decorative styling only; make them reflect page structure.

### `st.caption`

Use for small notes such as data freshness, units, caveats, and source attribution.

### `st.code`

Use for code output, generated config snippets, or reproducible commands. Avoid putting secrets in code blocks.

### `st.latex`

Use for formulas. Keep formulas close to the data or explanation they support.

### st json

Use for debugging structured data or showing API-like objects. Review output for secrets before displaying.

## Status and feedback

### `st.success`, `st.info`, `st.warning`, `st.error`

Use status calls consistently. Do not use success for unverified completion. Do not expose raw internal errors to untrusted users.

### `st.exception`

Useful for developer tools and internal debugging. Avoid exposing stack traces in public apps.

### `st.spinner`

Use around operations that may take noticeable time. Pair with caching when the operation repeats.

### `st.progress`

Use when progress is measurable. Do not fake progress for unknown-duration tasks unless labeled as activity.

### `st.status`

Use for multi-step work such as data loading, validation, generation, or deployment checks. Keep messages concise.

## Layout and containers

### `st.container`

Use to group content, preserve ordering, or update a block through a placeholder-like pattern.

### `st.empty`

Use as a placeholder for content that will be replaced, such as streaming text or delayed chart output.

### `st.columns`

Use for metrics, side-by-side charts, comparison panels, or action groups. Avoid too many columns on narrow screens.

### `st.sidebar`

Use for filters, app settings, navigation helpers, and secondary controls. Do not hide core outputs in the sidebar.

### `st.tabs`

Use for sibling views in the same task. Do not rely on tabs to avoid computing expensive content unless the code is explicitly gated.

### `st.expander`

Use for optional detail, advanced filters, logs, methodology, and debug information.

### `st.popover`

Use for compact secondary controls, especially filters or settings that should not occupy permanent page space.

### `st.dialog`

Use for edit, confirmation, preview, or focused workflows. Keep dialog state explicit.

### `st.fragment`

Use for isolated rerun regions or controlled refresh patterns. Reach for this after simpler forms/caches/state are insufficient.

## Inputs

### `st.button`

Use for one-shot actions. If an action updates state, use a small callback or explicit state assignment after click.

### `st.form` and `st.form_submit_button`

Use to batch related inputs and avoid rerunning expensive work on every field change.

### `st.checkbox` and `st.toggle`

Use for booleans. Toggle reads more like a setting; checkbox reads more like selection.

### `st.radio`

Use for a small number of visible mutually exclusive options.

### `st.selectbox`

Use for a longer single-choice list. Consider searchability and default choice.

### `st.multiselect`

Use for multi-choice filtering. Be careful with a default that selects hundreds of values.

### `st.slider`

Use for ranges or exploratory numeric filtering.

### `st.number_input`

Use when exact numeric entry matters.

### `st.text_input`

Use for short text such as search terms, IDs, and names.

### `st.text_area`

Use for prompts, notes, SQL fragments, JSON snippets, or long text. Validate before using as SQL or code.

### `st.date_input` and time widgets

Use for temporal filters. Clarify inclusive/exclusive date boundaries and timezone assumptions.

### `st.file_uploader`

Use for user-provided files. Validate size, type, schema, parsing errors, and privacy rules.

### `st.camera_input`

Use only when browser camera permissions and privacy are acceptable.

## Data elements

### `st.dataframe`

Use for interactive read-only data exploration. Configure columns for readable business output.

### `st.table`

Use for small static tables.

### `st.data_editor`

Use for editing data. Treat returned data as untrusted proposed changes until validated.

### `st.metric`

Use for headline numbers. Provide time range and definition when ambiguity exists.

### Column configuration

Use column config to format numbers, dates, links, images, progress, and select options. This improves app usability more than dumping raw dataframe columns.

## Charts

### Built-in line, area, bar, scatter, and map charts

Use for rapid prototypes or simple dashboards. They reduce dependency overhead.

### `st.altair_chart`

Use for declarative charts, layered encodings, facets, and strong grammar-of-graphics workflows.

### `st.plotly_chart`

Use for interactive charts with hover, zoom, click selection, and business dashboard familiarity.

### `st.pyplot`

Use for Matplotlib figures. Always pass a figure object. Avoid relying on global pyplot state.

### `st.pydeck_chart`

Use for geospatial visualizations when location is central to the task.

### `st.graphviz_chart`

Use for simple graph diagrams. For complex graph workflows, consider specialized visualization libraries.

## Media

### `st.image`

Use for local or uploaded images. Consider resizing and privacy.

### `st.audio`, `st.video`

Use for media playback. Avoid huge embedded files in apps that deploy over limited bandwidth.

## Chat

### `st.chat_message`

Use to render conversation messages. Store role/content in session state or a persisted store.

### `st.chat_input`

Use for chat-style prompt entry. Combine with cost/rate controls for LLM apps.

### Streaming output

Use placeholders or supported write-stream behavior depending on Streamlit version and provider interface. Preserve the final response in message history.

## State and URL

### `st.session_state`

Use for per-session UI/workflow state. Initialize before use and avoid storing large shared resources.

### `st.query_params`

Use for shareable filters, selected IDs, page state, or deep links. Validate query parameters before trusting them.

## Control flow

### `st.stop`

Use after missing required input, failed auth, invalid upload, or unrecoverable state.

### `st.rerun`

Use sparingly after state changes that require immediate full rerender. Guard against loops.

## Cache

### `st.cache_data`

Use for data values. Add TTL or manual invalidation when freshness matters.

### `st.cache_resource`

Use for clients, models, engines, and shared resources. Ensure no user-specific authorization boundary is hidden inside the resource.

## Connections

### `st.connection`

Use when a supported connection type fits the deployment model. Keep connection names and secrets documented.

### Custom connection wrappers

Use cached factory functions for unsupported SDK clients. Add timeout and error handling.

## Testing

### `streamlit.testing.v1.AppTest`

Use for app start, widget interaction, and UI assertions. Keep tests focused on your app behavior, not Streamlit internals.

## Decision rule

When choosing between APIs, prefer:

1. native Streamlit feature;
2. a simple wrapper around native feature;
3. official/maintained component or chart library;
4. custom HTML/CSS/JS only when necessary and reviewed for safety/maintenance.
