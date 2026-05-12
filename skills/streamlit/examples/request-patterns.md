# Request Patterns

Use these examples to calibrate activation and output style.

## Activate

User: "Create a Streamlit dashboard for onboarding funnel data."

Expected mode: `new-app`, `ui`, `data-cache`.

Good response: propose a minimal app structure, include runnable code, use cache for data loading, include filters, metrics, table, download, and validation.

---

User: "My Streamlit checkbox keeps resetting."

Expected mode: `state-debug`, `troubleshooting`.

Good response: explain likely rerun/key/session-state issue, show smallest patch using stable key and `setdefault`, add verification steps.

---

User: "Add login to my Streamlit app."

Expected mode: `deployment`, `security-review`.

Good response: ask/infer identity provider and deployment target when needed; provide auth guard shape; warn about access-control boundary; do not fake provider configuration.

---

User: "Build a ChatGPT-like UI in Streamlit with streaming."

Expected mode: `llm-chat`.

Good response: use `st.chat_message`, `st.chat_input`, session messages, streaming placeholder, and provider abstraction; discuss privacy and cost.

---

User: "Review this app before production."

Expected mode: `review`, `security-review`, `deployment`, `testing`.

Good response: severity-ranked findings, data/cache/state/security/deployment gates, measured vs not-run validation.

## Do not activate

User: "Write a pandas script to clean this CSV."

Reason: not Streamlit-specific unless the output is a Streamlit app.

---

User: "Build a Flask API."

Reason: backend-only app.

---

User: "Create a React dashboard."

Reason: frontend-only non-Streamlit task.

---

User: "Analyze this dataset and tell me the average." 

Reason: pure data analysis; use Streamlit only if user asks for an app/dashboard.

## Ambiguous

User: "Create a dashboard."

If user context suggests Python/Streamlit, proceed with a Streamlit assumption and state it. Otherwise ask which framework only if framework choice matters.

---

User: "Deploy my app."

If files show Streamlit or the user says Streamlit, activate. Otherwise ask or inspect project type.

## Edge cases

User: "Copy this Streamlit skill from another repo into my Apache repo."

Activate for source hygiene and refuse unsafe copying if license is unclear. Offer a clean-room rewrite.

---

User: "Cache each user's private account data globally so it is faster."

Activate but treat as security risk. Use user/tenant cache keys or avoid shared cache.
