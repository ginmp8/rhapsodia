# Authentication, Secrets, and Security

## Secrets

Use `st.secrets` or environment-backed deployment secrets. Never hardcode tokens, passwords, private keys, connection strings, or OAuth client secrets in app code, examples, logs, screenshots, reports, or committed files.

## Secret structure

Keep secrets grouped by system:

```toml
[database]
url = "postgresql://app_user:replace-me@db.example.com:5432/app_db"

[auth]
client_id = "replace-with-oauth-client-id"
client_secret = "replace-with-managed-secret-value"
```

Use placeholder values in examples and clearly mark them as placeholders.

## Authentication

For apps requiring identity, use Streamlit's authentication features when appropriate and configure the identity provider through secrets/config. Check login state before showing private content.

## Authorization

Authentication proves identity; authorization decides what the user can access. Implement role checks for pages, records, actions, and downloads. Do not rely only on hiding UI controls; protect backend actions too.

## Dangerous actions

For deletes, approvals, account changes, or writes:

- require authentication;
- check authorization;
- show a confirmation summary;
- use idempotency or duplicate guards;
- log actor, timestamp, target, and result;
- show safe success/failure messages.

## File security

Treat uploads as untrusted. Validate file type and size. Avoid executing uploaded content. Sanitize filenames. Keep parsed previews limited.

## HTML and components

Avoid custom HTML/JavaScript unless necessary. If using HTML, avoid injecting untrusted user content. Prefer native Streamlit widgets and components.

## Error handling

Show user-safe messages. Log technical details server-side when appropriate. Do not display raw secrets, headers, connection strings, SQL with sensitive literals, or stack traces in production-facing apps.

## Security review checklist

- No hardcoded secrets.
- Secrets loaded through approved mechanisms.
- User identity checked before private data appears.
- Role checks guard actions and data, not only navigation.
- Uploads are validated.
- External writes are explicit and auditable.
- Downloaded files do not leak hidden columns or secrets.
- Debug mode and detailed errors are disabled or restricted in production.
