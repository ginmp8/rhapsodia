# Security Review Standard for Secrets

## Contract identity

Policy version: `2`

This policy separates potential impact (**severity**) from evidentiary certainty (**confidence**) so uncertain authenticity does not distort risk ranking.

## Secret and credential taxonomy

Treat these as credential-bearing or secret material when context supports it:

- API keys, access tokens, OAuth client secrets, refresh tokens, and webhook/signing secrets;
- passwords, database credentials, and DSNs/connection strings with embedded credentials;
- cloud access keys and secret keys;
- private keys and certificates containing private material;
- session cookies, bearer tokens, JWTs, and authorization headers;
- encryption keys, HMAC keys, and other values whose disclosure enables access, impersonation, signing, decryption, or privilege.

Do not classify public identifiers, tenant/account IDs, hostnames, checksums, public keys, or non-secret hashes as credentials without additional evidence.

## Finding taxonomy

Prefer the narrowest applicable category:

- `hardcoded_credential`
- `private_key_material`
- `credential_in_log`
- `credential_in_example_or_docs`
- `credential_in_client_artifact`
- `credential_in_ci_or_iac`
- `credential_bearing_connection_string`
- `unsafe_secret_fallback`
- `weak_secret_redaction`
- `long_lived_static_credential`

Scanner-specific rule IDs may be preserved as detection evidence, but the final review may map them to one of these semantic categories.

## Severity model

### Critical

Use `critical` when the evidence indicates a credential or private key is directly exposed **and** one or more high-impact conditions apply, such as production/admin scope, broadly accessible/public distribution, client-side embedding, or material signing/decryption authority.

Do not use `critical` merely because a token matches a known prefix.

### High

Use `high` when a likely credential is exposed in source, configuration, CI/CD, IaC, logs, tests, documentation, or another shared surface and misuse could provide meaningful unauthorized access.

### Medium

Use `medium` for credential-handling defects that create material risk but lack strong evidence of an immediately usable exposed credential, such as unsafe plaintext storage, static shared credentials, or insecure fallback behavior.

### Low

Use `low` for limited-impact hygiene defects such as incomplete masking or examples that encourage weak handling but do not contain likely usable credentials.

## Confidence model

### Confirmed

Use `confirmed` only when the artifact itself establishes the secret nature of the material without requiring external authentication, for example valid private-key material or an explicitly supplied fact that the credential is real.

### Likely

Use `likely` when format and context strongly indicate credential material, such as a provider-specific token form, credential-bearing connection string, or authorization token in a real code path.

### Possible

Use `possible` when the value is suspicious but authenticity or meaning is ambiguous. Synthetic examples, truncated/redacted strings, generic entropy matches, and ambiguous assignments normally stay here unless corroborated.

Never attempt authentication merely to raise confidence.

## Severity tie-breakers

When two severities seem plausible, evaluate in this order:

1. reachable exposure surface: public/client-side/shared-log > restricted internal source > local developer-only;
2. privilege/scope: admin/signing/production > write > read > narrowly scoped test;
3. environment: production > shared non-production > isolated local test;
4. credential lifetime: long-lived/reusable > short-lived/ephemeral;
5. evidence of distribution: history/logs/artifacts/shared docs increase exposure breadth.

If evidence is missing, lower **confidence** before lowering potential-impact severity solely for uncertainty.

## Strong indicators

Examples of stronger evidence include:

- private-key blocks or private-key files;
- provider-specific credential formats in credential-bearing context;
- full connection strings with username and password;
- bearer/session material in logs or headers;
- high-entropy values assigned to secret-like variables plus runtime usage evidence.

## Weak signals

Treat these as non-findings or `possible` candidates unless corroborated:

- secret-like variable names with no assigned credential value;
- clearly synthetic example values;
- random IDs with no authentication semantics;
- hashes/checksums;
- public identifiers;
- values already redacted so strongly that authenticity cannot be inferred.

## Evidence rules

Every reported finding needs:

- exact location or bounded section;
- the narrowest stable rule/category;
- redacted evidence that does not reproduce a usable credential;
- severity and confidence justified by the available context;
- remediation linked to the defect.

A detector hit alone is insufficient for `confirmed` confidence.

## Ordering and deduplication

Canonical final ordering:

`critical -> high -> medium -> low`, then path, line, rule, finding ID.

When multiple detector rules point to the same source value, prefer the most specific rule. Do not inflate finding count by reporting an entropy match and a provider-specific match separately for the same credential.

## Coverage semantics

- `complete`: every requested and supported surface was inspected with no scanner skips or unavailable material.
- `partial`: one or more requested/material surfaces were skipped, inaccessible, unsupported, or unavailable.

A partial review may still contain valid findings. It may not support a blanket clean conclusion.
