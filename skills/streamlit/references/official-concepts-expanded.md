# Official Concept Expansion

These notes synthesize official concept areas into operational guidance. They are not copied from docs.

## Running your app

Official reference: https://docs.streamlit.io/develop/concepts/architecture/run-your-app

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on running your app, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Streamlit architecture

Official reference: https://docs.streamlit.io/develop/concepts/architecture/architecture

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on streamlit architecture, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Caching concept

Official reference: https://docs.streamlit.io/develop/concepts/architecture/caching

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on caching concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Session State concept

Official reference: https://docs.streamlit.io/develop/concepts/architecture/session-state

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on session state concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Forms concept

Official reference: https://docs.streamlit.io/develop/concepts/architecture/forms

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on forms concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Fragments concept

Official reference: https://docs.streamlit.io/develop/concepts/architecture/fragments

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on fragments concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Widget behavior

Official reference: https://docs.streamlit.io/develop/concepts/architecture/widget-behavior

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on widget behavior, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Multipage apps overview

Official reference: https://docs.streamlit.io/develop/concepts/multipage-apps/overview

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on multipage apps overview, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Page and navigation

Official reference: https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on page and navigation, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Pages directory

Official reference: https://docs.streamlit.io/develop/concepts/multipage-apps/pages-directory

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on pages directory, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Layouts and containers

Official reference: https://docs.streamlit.io/develop/concepts/design/layouts-and-containers

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on layouts and containers, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Buttons concept

Official reference: https://docs.streamlit.io/develop/concepts/design/buttons

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on buttons concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Dataframes concept

Official reference: https://docs.streamlit.io/develop/concepts/design/dataframes

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on dataframes concept, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Multithreading

Official reference: https://docs.streamlit.io/develop/concepts/design/multithreading

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on multithreading, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Timezone handling

Official reference: https://docs.streamlit.io/develop/concepts/design/timezone-handling

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on timezone handling, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Connecting to data

Official reference: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on connecting to data, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Secrets management

Official reference: https://docs.streamlit.io/develop/concepts/connections/secrets-management

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on secrets management, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## User authentication

Official reference: https://docs.streamlit.io/develop/concepts/connections/authentication

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on user authentication, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Security reminders

Official reference: https://docs.streamlit.io/develop/concepts/connections/security-reminders

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on security reminders, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## App testing

Official reference: https://docs.streamlit.io/develop/concepts/app-testing

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on app testing, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Configuration options

Official reference: https://docs.streamlit.io/develop/concepts/configuration/options

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on configuration options, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Theming

Official reference: https://docs.streamlit.io/develop/concepts/configuration/theming

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on theming, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”

## Static file serving

Official reference: https://docs.streamlit.io/develop/concepts/configuration/serving-static-files

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
When working on static file serving, connect the Streamlit concept to code structure, state ownership, and validation. Use the official page for exact version-specific details.

**Implementation pattern**
1. Configure the page at the top when useful.
2. Initialize required session state keys.
3. Load shared resources with `st.cache_resource` and data with `st.cache_data`.
4. Place filters and navigation in the sidebar or a dedicated control area.
5. Render metrics, tables, charts, and detail views from explicit variables.
6. Put risky actions behind forms, buttons, dialogs, or confirmations.
7. Add smoke tests for expected UI state and at least one error path.

**Anti-patterns**
- Long scripts with mixed I/O, UI, business rules, and writes in one block.
- Recomputing expensive data because the cache boundary was omitted.
- Using globals as if each user had a separate process.
- Introducing custom components before exhausting native Streamlit layout and widget options.
- Showing raw exceptions or secret-derived values to end users.

**Validation prompts**
- Ask: “What reruns this app, and what persists across reruns?”
- Ask: “Which work is per-user, which work is shared, and which work is external I/O?”
- Ask: “Can this flow be tested without a browser?”
- Ask: “What happens if two users interact with this at the same time?”
