# Security Review Standard for Secrets

## Scope

Apply this standard to source code, configuration, infrastructure-as-code, CI/CD definitions, test fixtures, sample payloads, screenshots, documentation, and generated artifacts.

## What counts as a secret

Treat the following as secrets or sensitive credentials:

- API keys and access tokens
- OAuth client secrets and refresh tokens
- Database passwords and DSNs with embedded credentials
- Cloud provider access keys and secret keys
- Private keys, certificates with private material, and PEM blocks
- Session cookies, JWTs, bearer tokens, and authorization headers
- Webhook secrets, signing secrets, encryption keys, and HMAC keys

## Severity model

### Critical

Use `critical` when a likely real credential appears directly in code, config, versioned files, client-side code, or public artifacts, especially when it grants production or administrative access.

### High

Use `high` when a likely real credential is exposed internally, in CI/CD, IaC, tests, or documentation, or when logs reveal authentic authorization material.

### Medium

Use `medium` for unsafe storage patterns that are not obviously live secrets yet still create meaningful risk, such as local files with real-looking credentials, broad default credentials, or plaintext secrets in internal configs.

### Low

Use `low` for weak practices with limited immediate exploitability, such as unnecessary secret handling complexity, incomplete redaction, or examples that encourage insecure patterns.

### Needs verification

Use `needs verification` when the string is suspicious but may be placeholder, synthetic, truncated, redacted, or otherwise non-live.

## Review heuristics

Treat these as strong indicators:

- `-----BEGIN ... PRIVATE KEY-----`
- Known provider token prefixes
- Full connection strings containing username and password
- Long random strings assigned to variables named secret-like terms
- Secrets present in logs or headers

Treat these as likely false positives unless other evidence exists:

- Obvious placeholder values
- Random test IDs without authentication meaning
- Hash digests used for checksums
- Public identifiers such as tenant IDs, account IDs, or hostnames without credentials

## Minimum acceptable recommendation

At minimum, recommend moving the value out of code and into deployment-time configuration. Prefer stronger recommendations when the runtime platform supports:

1. managed identity or workload identity
2. managed secret store
3. environment variable injection

## Mandatory post-exposure actions

When a likely real secret is exposed, recommend all of the following:

1. rotate or revoke the secret
2. search for reuse across logs, docs, pipelines, and neighboring repositories
3. reduce permission scope if possible
4. add detection or push protection to prevent recurrence
