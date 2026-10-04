# Execution, State, and Reruns

## Mental model

Streamlit normally executes the script top-to-bottom. Widget interactions can update client/widget state and trigger a rerun. Design top-level code to be safe when repeated.

## State ownership

- Use `st.session_state` for per-session state.
- Use databases/object stores for durable state.
- Use cached resources for intentionally shared process-level resources.
- Avoid mutable module globals for user-specific state.

Initialize state before widgets that consume it. Use stable business identifiers for keys when lists can reorder.

## Widgets are not a security boundary

Options, min/max bounds, disabled controls, validation hints, and other browser constraints primarily improve UX. Revalidate values in Python before authorization decisions, database writes, file paths, quotas, financial limits, or tenant selection.

## URL binding and persistence

When the installed version supports `bind="query-params"`, prefer it over hand-written query-param synchronization for shareable widget state. Use `persist_state` when supported and the value should survive conditional rendering/page changes without appearing in the URL. Record version evidence before introducing either API.

Do not mix bound query params with competing manual writes to the same parameter.

## Callbacks

Callbacks execute before the subsequent script rerun. Keep them small and explicit: state transitions, reset actions, or targeted rerun/navigation. Avoid hiding slow network/database workflows in callbacks unless the operation is intentionally guarded and observable.

## Forms and no-rerun controls

Use forms when multiple values should commit together or intermediate changes would trigger expensive work. Use supported `on_change="ignore"` behavior when one control should update in the browser but Python should not rerun until another action occurs.

## Fragments

Use `st.fragment` for sections with an independent rerun cadence. When supported, keyed fragment reruns can target one or several registered fragments from callbacks. Do not assume a fragment key exists if it was not rendered in the last completed full-app run.

Use parallel fragments only for independent work. Treat them as concurrent execution: do not unsafely mutate the same session-state key or shared mutable object from multiple parallel fragments.

## Dialogs and focused flows

Dialogs are suitable for confirmations, detail previews, and compact forms. Keep critical validation/error state visible to the page flow that depends on it.

## Side effects

Protect writes with explicit actions. For retried or externally delivered operations, use idempotency/deduplication where the backend supports it. A button is true only for the run caused by its click; persist durable workflow state separately.

## Debug procedure

1. Identify the interaction that triggers the surprising rerun.
2. Inspect relevant session/widget state and keys.
3. Separate repeated computation from repeated side effects.
4. Move expensive deterministic work behind the correct cache.
5. Choose form/no-rerun/fragment boundaries only when they match UX semantics.
6. Add AppTest coverage when the behavior is representable headlessly; use browser/E2E for browser-owned behavior.
