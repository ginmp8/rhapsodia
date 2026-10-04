# Authentication, Secrets, and Security

## Secrets

Use `st.secrets` or deployment-managed environment secrets. Never hardcode tokens, passwords, private keys, database credentials, OAuth client secrets, or real production identifiers in source, examples, logs, screenshots, reports, committed config, or generated fixtures.

## Authentication

For user identity, prefer Streamlit's supported OIDC flow (`st.login`, `st.user`, `st.logout`) when the resolved version and deployment support it. Do not implement authentication by comparing `st.text_input(type="password")` with a shared secret.

OIDC proves identity. It does not prove the user may access a page, record, tenant, export, or mutation.

## Authorization

Enforce authorization at the backend action/data boundary. Hiding a page, button, dataframe column, or navigation entry is not sufficient. Check actor + action + resource before protected reads/writes/downloads.

## Client input trust

Treat widget-returned values as untrusted for security-sensitive decisions even when the widget declares `options`, `min_value`, `max_value`, `required`, validation rules, or `disabled=True`. Revalidate allowed values and bounds in Python immediately before the protected operation.

## Dangerous actions

For deletes, approvals, account changes, payments, outbound messages, or external writes:

- authenticate;
- authorize;
- summarize/confirm when consequence warrants it;
- use idempotency or duplicate guards;
- record actor/target/result in appropriate server-side logs;
- return user-safe errors without secrets or raw headers.

## Files and HTML/JavaScript

Treat uploads as untrusted. Validate type/size/content as needed and do not execute uploaded material. Avoid injecting untrusted HTML or JavaScript. For Components v2, JavaScript is trusted application code, not a sandbox for arbitrary user content; see `references/custom-components-v2.md`.

## Cached/private data

Do not leak user/tenant data through shared caches, shared mutable resources, hidden dataframe columns, downloads, or session-to-session global state. Remove sensitive fields before sending data to the frontend; visual hiding is not data removal.

## Production review

Confirm secrets loading, identity provider redirect configuration, backend authorization, upload/download boundaries, error visibility, cache isolation, server configuration, and observability. Do not claim a deployment secure from static code inspection alone.
