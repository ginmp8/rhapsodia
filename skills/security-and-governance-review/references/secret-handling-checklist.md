# Secret Handling Checklist

Use this checklist for `secret-handling-review`.

## Inspect

- Hardcoded passwords, api keys, bearer tokens, oauth client secrets, webhook secrets, signing keys, private keys, certificates, cookies, session ids, and database connection strings.
- Secrets split across literals in the same file.
- Base64 or encoded credentials used as credential storage.
- `.env`, `.npmrc`, `.pypirc`, cloud credential files, service-account json, kubeconfig, ssh keys, and local config examples.
- Secrets in tests, fixtures, examples, markdown docs, screenshots, generated reports, expected outputs, package templates, and validator outputs.
- Sensitive logging of authorization headers, cookies, jwt values, session ids, tokens, full connection strings, request bodies, or exception objects carrying secrets.
- Default credentials, fallback secrets, `changeme` defaults, and bootstrap tokens.

## Classify safely

Treat as confirmed risk:

- Provider-shaped tokens or private key blocks.
- Connection strings with embedded passwords or access keys.
- Concrete credential values assigned to credential-like names.
- Logging that prints sensitive fields from real runtime data.

Treat as potential risk:

- Placeholder samples that normalize unsafe practice.
- Credential-like variables with non-placeholder values that cannot be validated.
- Redaction functions without tests.
- Documentation that encourages copying secrets into files.

Treat as evidence limitation:

- Config values sourced externally but no deployment policy is available.
- Secret scanners are unavailable for a repository-scale claim.
- The review lacks history, logs, or environment configuration.

## Masking rules

- Never output the full value.
- For short values, use `[masked secret]`.
- For longer values, use at most the first 3 and last 3 visible characters, for example `abc...xyz`.
- For private keys, output only `[masked private key block]`.
- Do not include raw screenshots or copied blocks containing secrets.

## Remediation guidance

- Rotate or revoke exposed real credentials.
- Remove secrets from code, docs, examples, templates, reports, expected outputs, and logs.
- Move runtime secrets to workload identity or a managed secret store when possible; otherwise inject via deployment-time environment variables.
- Keep `.env.example` free of real values.
- Add automated secret scanning and redaction tests.
- Redact logs at field boundaries and avoid logging full request/response payloads for sensitive operations.
- Audit blast radius, scopes, and downstream systems after exposure.
