# Streamlit Request Patterns

Use these examples to calibrate activation and response style.

## Activate

### Build a dashboard

User request: "Create a Streamlit dashboard for onboarding funnel data."

Expected behavior: propose a minimal app structure, include runnable code, use `st.cache_data` for data loading, include filters, metrics, table, download behavior, and validation.

### Fix state behavior

User request: "My checkbox keeps resetting in Streamlit."

Expected behavior: explain likely rerun, key, or `st.session_state` issue; show the smallest patch with stable keys and state initialization; add verification steps.

### Add authentication

User request: "Add login to my Streamlit app."

Expected behavior: identify identity provider and deployment target when needed; provide an auth guard shape; warn that authentication is not the same as row-level authorization.

### Build a chat UI

User request: "Build a ChatGPT-like UI in Streamlit with streaming."

Expected behavior: use `st.chat_message`, `st.chat_input`, message history in session state, a streaming surface, and a model-client boundary; discuss privacy and cost controls.

### Review for production

User request: "Review this Streamlit app before production."

Expected behavior: return severity-ranked findings, state/cache/security/deployment gates, and separate executed validation from recommended validation.

## Do not activate

### Pure pandas work

User request: "Write a pandas script to clean this CSV."

Reason: not Streamlit-specific unless the output is a Streamlit app or dashboard.

### Backend-only service

User request: "Build a Flask API."

Reason: Streamlit is not the primary framework.

### Non-Streamlit frontend

User request: "Create a React dashboard."

Reason: frontend-only non-Streamlit task.

### Plain data analysis

User request: "Analyze this dataset and tell me the average."

Reason: use Streamlit only if the user asks for an app, dashboard, or interactive UI.

## Ambiguous

### Dashboard without framework

User request: "Create a dashboard."

Behavior: if conversation context suggests Python or Streamlit, proceed with a Streamlit assumption and state it. If framework choice materially affects the answer, ask which framework to use.

### Deploy an app

User request: "Deploy my app."

Behavior: activate only when files, logs, prior context, or user language indicate Streamlit. Otherwise inspect project type or ask for the app framework.

## Edge cases

### Copying another skill

User request: "Copy this Streamlit skill from another repo into my Apache repo."

Behavior: activate for source hygiene, avoid copying a third-party skill with unclear license, and offer a clean-room rewrite from official sources.

### Unsafe caching

User request: "Cache each user's private account data globally so it is faster."

Behavior: activate but classify as a security risk. Use user/tenant cache keys, session-only state, or avoid shared cache depending on sensitivity.
