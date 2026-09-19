# Secret Handling Checklist

Use this checklist for `secret-handling-review`.

## Absolute output rule

**Never print, quote, log, copy, hash-as-display, or otherwise reproduce a complete secret value in review output.** This applies even when the user supplied the value or the target file is local. Use `[masked secret]` or `[masked private key block]`. Do not preserve prefix/suffix fragments as a default redaction strategy.

The bundled scanner uses deterministic content omission/fingerprints so repeated runs do not expose additional fragments.

## Inspect

- Hardcoded passwords, api keys, bearer tokens, oauth client secrets, webhook secrets, signing keys, private keys, certificates, cookies, session ids, and database connection strings.
- Secrets split across literals in the same file.
- Base64/encoded credentials used as credential storage.
- `.env`, `.npmrc`, `.pypirc`, cloud credential files, service-account json, kubeconfig, ssh keys, and local config examples.
- Secrets in tests, fixtures, examples, markdown docs, screenshots, generated reports, expected outputs, package templates, and validator outputs.
- Sensitive logging of authorization headers, cookies, jwt/session/token values, full connection strings, request bodies, or exception objects carrying secrets.
- Default credentials, fallback secrets, `changeme` defaults, and bootstrap tokens.

## Protect source material

- Credentials, `.env`, and private-key files are protected-unread by default for snapshotting; do not ingest their contents merely to create a receipt.
- Fixtures and expected outputs are protected from mutation; identity may be hash-only when necessary.
- Never modify or delete protected files during a review.
- If inspection of a protected source is essential, require explicit authorization and still apply the absolute output rule.

## Classification

Use `confirmed` only when evidence establishes the unsafe condition actually claimed, for example a known-live credential exposed in a public artifact with authoritative confirmation. Pattern matching alone is `suspicious-pattern`.

Use `needs-verification` when a credential-shaped value cannot be safely/authentically verified. Placeholders such as `example-token` or `your_api_key_here` are not confirmed leaks; they may be low-severity sample-hygiene findings if they normalize unsafe practice.

## Remediation

- If a real credential is confirmed exposed: revoke/rotate, remove from artifacts/logs, and assess blast radius/scopes.
- Move runtime secrets to workload identity or a managed secret store when possible; otherwise inject through a controlled deployment-time secret mechanism.
- Keep `.env.example` free of real values.
- Add automated secret scanning/redaction tests using fake credentials.
- Redact logs at field boundaries; avoid logging full sensitive request/response payloads.
