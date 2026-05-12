# App Architecture

## Purpose

Design Streamlit apps that stay understandable after the first prototype. Use this reference for new apps, refactors, multipage structure, code organization, and production-oriented design.

## App types and default architecture

### Exploratory dashboard

Best for analytics, KPIs, filters, and charts. Keep read-only data loading cached. Place filters in the sidebar or top controls. Render the same filtered dataset through metrics, tables, and charts to avoid inconsistent slices.

### Guided workflow

Best for onboarding, review queues, approval flows, and internal tools. Model the flow as explicit steps in `st.session_state`. Use `st.form` for step inputs and buttons for transitions. Save only after a confirmation step.

### Data editor app

Best when users need to correct or annotate tabular data. Use `st.data_editor`, typed `st.column_config`, and a separate save action. Diff edited data against the source before writing changes.

### Chat or LLM app

Best for conversational interfaces, retrieval, summarization, or assistants. Store visible chat history in session state. Stream responses with `st.write_stream` when the backend supports incremental output. Keep retrieval and model clients cached as resources.

### Operational tool

Best for support, administration, or internal operations. Treat every external write as high risk. Add permission checks, audit fields, confirmations, and visible result states.

## File layout patterns

### Single-file app

Use for prototypes, demos, and small dashboards. Keep helper functions above UI code. Avoid hidden global mutation. Once the file exceeds roughly a few screens of logic, move pure logic into modules.

### Modular app

Suggested layout:

```text
app.py
source package
  data module
  chart module
  state module
  action module
  security module
  ui modules
pages/
  01_dashboard.py
  02_admin.py
.streamlit/
  config.toml
```

Use a data module for loading and transformations, an actions module for side effects, and UI modules for reusable rendering functions. Keep Streamlit calls out of pure data functions when possible so tests can run without Streamlit.

## Control-plane pattern

At the top of each app:

1. Imports and constants.
2. `st.set_page_config`.
3. session-state initialization.
4. cached resources and data functions.
5. UI controls.
6. derived data.
7. output rendering.
8. actions and result messages.

## State boundaries

Use session state for user selections, wizard step, selected IDs, edited drafts, chat messages, and transient UI decisions. Do not store unbounded data, secrets, database engines, or large model objects in session state. Use cache resources for shared clients and caches for computed data.

## Side-effect boundaries

Any external mutation should answer these questions before code is written:

- What user action triggers it?
- Can a rerun repeat it accidentally?
- Is there an idempotency key or duplicate guard?
- What confirms success to the user?
- What logs or audit fields are created?
- How is failure displayed without exposing sensitive details?

## Multipage decision

Use a multipage app when pages represent distinct jobs, user roles, or mental contexts. Do not split merely because a file is long; refactor into functions/modules first. Use pages when navigation improves comprehension.

## App review checklist

- Page title and layout are configured.
- Script can rerun safely without repeating writes.
- Expensive I/O is cached or moved behind explicit actions.
- State keys are initialized in one place.
- Widgets have meaningful labels and stable keys.
- External writes have confirmation and error handling.
- Secrets are read from `st.secrets` or environment-backed configuration, not source files.
- Tests or smoke checks cover at least one happy path and one error path.
