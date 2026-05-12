# Anti-patterns and Safer Alternatives

## Side effects at top level

Bad: database writes or API mutations run as soon as the script reruns.

Safer: put writes behind `st.form_submit_button`, `st.button`, dialog confirmation, and idempotency checks.

## Globals as user state

Bad: global variables store selected user, current record, chat messages, or filters.

Safer: use `st.session_state` for per-session values and cached resources for shared clients.

## Unbounded cache

Bad: cache every query forever without tenant, user, filters, or TTL.

Safer: include scope and filters in function parameters, add TTL, and avoid caching sensitive user-specific results unless access is scoped.

## Custom HTML first

Bad: build custom HTML/CSS/JS for common controls.

Safer: use Streamlit native layout, widgets, markdown, badges, status elements, and components only when native APIs cannot satisfy the need.

## Hidden callback workflows

Bad: callbacks perform network calls, writes, and navigation without visible state.

Safer: callbacks only update state; main script renders the next action and error/success states visibly.

## Data editor without save semantics

Bad: editable table changes are treated as persisted automatically.

Safer: compute diff, validate, preview, and save explicitly.

## Secrets in examples

Bad: examples contain realistic tokens, passwords, or connection strings.

Safer: use placeholders and `st.secrets` lookup with clear instructions.

## No empty states

Bad: charts/tables fail or look broken when no data matches filters.

Safer: explicitly detect empty data and show next-step guidance.

## Overbuilt multipage app

Bad: split a small app into many pages before workflow is understood.

Safer: start with one page and modules; add pages when user tasks are truly separate.

## Untestable monolith

Bad: data loading, transformation, UI, and writes are interleaved.

Safer: pure functions for transformations, isolated I/O functions, thin UI layer, and AppTest for page behavior.
