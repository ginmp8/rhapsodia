# Official Deployment Expansion

Task-oriented notes for deployment and operations. Use official pages for current platform details.

## Community Cloud overview

Official reference: https://docs.streamlit.io/deploy/streamlit-community-cloud

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For community cloud overview, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Deploy from GitHub

Official reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For deploy from github, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Manage app dependencies

Official reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For manage app dependencies, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Manage secrets

Official reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For manage secrets, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Docker deployment concepts

Official reference: https://docs.streamlit.io/deploy/tutorials/docker

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For docker deployment concepts, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Kubernetes deployment concepts

Official reference: https://docs.streamlit.io/deploy/tutorials/kubernetes

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For kubernetes deployment concepts, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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

## Snowflake deployment

Official reference: https://docs.streamlit.io/deploy/snowflake

**Operational model**
Streamlit apps are Python programs whose visible UI is the result of executing the script. Treat every user interaction as a possible rerun and keep the script idempotent. The assistant should design apps around a small number of explicit state transitions instead of hidden mutable globals.

**How to help**
- Start by identifying the app's main workflow: data exploration, dashboarding, CRUD-style editing, guided form, chat, model inference, or operational tool.
- Map every widget to a specific state variable or immediate display decision.
- Separate pure transformations from I/O. Pure functions are easier to cache, test, and reuse.
- Prefer simple pages and clear sections before adding multipage routing or custom components.
- Document assumptions about data freshness, concurrent users, credentials, and deployment environment.

**Specific focus for this topic**
For snowflake deployment, identify platform assumptions, secrets/config, dependency declarations, startup command, logs, network access, and smoke-test evidence.

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
