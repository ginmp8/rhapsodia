# Layout, Navigation, and Pages

## Layout principles

Use layout to express decision hierarchy. A user should understand the current question, available controls, and result area without reading code.

## Common layout patterns

### Sidebar filters

Use for global controls that affect most of a page. Keep the sidebar short; group advanced filters in expanders.

### Top control strip

Use columns at the top when filters are few and important. This keeps the result area visually connected to controls.

### KPI row plus detail tabs

Use columns for metrics and tabs for drilldowns. Keep expensive charts in tabs only when users need all tabs loaded together; otherwise use pages or conditional rendering.

### Master-detail

Use a table or list selection on the left and details on the right. Store selected ID in session state.

### Wizard

Represent steps as explicit session-state values. Render one step at a time and keep transitions controlled by buttons/forms.

## Containers

Use `st.container` to group related UI and `st.empty` to replace content after an action. Avoid deeply nested containers unless they clarify ownership.

## Tabs

Tabs are useful for alternative views of the same data. They are less ideal for unrelated workflows. If each tab has independent state, URL, role, or data source, use pages.

## Expanders and popovers

Use expanders for optional details and diagnostics. Use popovers for compact controls. Do not hide primary actions or critical errors in collapsed UI.

## Multipage apps

Use programmatic navigation when page definitions depend on roles, feature flags, or dynamic availability. Use the pages directory for simple static page sets. Keep shared utilities outside page files.

## Page state

Cross-page state should be explicit and small: selected entity, current role, filter set, or authenticated user. Avoid stuffing full datasets into session state for page handoff.

## Theme and configuration

Use `.streamlit/config.toml` for theme and server/client defaults. Treat config as deployment input, not hidden business logic. Document settings that affect security, uploads, CORS, or error visibility.

## UX review

- Is the page title actionable?
- Does the first screen show the app purpose?
- Are controls grouped by what they affect?
- Are empty, loading, error, and success states visible?
- Is there a path back from detail states?
- Would the app still be usable on a narrower screen?
