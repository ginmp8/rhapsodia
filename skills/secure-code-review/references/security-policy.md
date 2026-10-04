# Security Review Standard for Secrets

## Contract identity

Policy version: `3`

This policy separates detector signals, evidentiary confidence, and potential impact severity.

## Secret and credential taxonomy

Treat these as credential-bearing or secret material when context supports it:

- API keys, access tokens, OAuth client/refresh secrets, webhook/signing secrets;
- passwords, database credentials, and credential-bearing DSNs/connection strings;
- cloud access keys and secret keys;
- private keys and certificates containing private material;
- session cookies, bearer tokens, JWTs, and authorization headers;
- encryption/HMAC/signing keys and values whose disclosure enables access, impersonation, signing, decryption, or privilege.

Do not classify public identifiers, tenant/account IDs, hostnames, checksums, public keys, or non-secret hashes as credentials without additional evidence.

## Detector signal is not final severity

Scanner rule strength, provider prefix, token length, and entropy are detection evidence only. They do not determine final severity. A generic high-entropy assignment must not become `high` merely because it looks random.

Final assessment requires semantic context: exposure surface, privilege/scope, environment, authority, lifetime, distribution breadth, and credential meaning.

## Finding taxonomy

Prefer the narrowest applicable category:

- `hardcoded_credential`
- `private_key_material`
- `credential_in_log`
- `derived_credential_in_log`
- `credential_in_example_or_docs`
- `credential_in_client_artifact`
- `credential_in_build_artifact`
- `credential_in_git_history`
- `credential_in_ci_or_iac`
- `credential_bearing_connection_string`
- `unsafe_secret_fallback`
- `unsafe_secret_persistence`
- `weak_secret_redaction`
- `long_lived_static_credential`
- `privileged_untrusted_secret_flow`
- `agent_output_credential_exposure`

Scanner rule IDs may be retained as detector evidence, but the final report should map them to semantic categories when possible.

## Severity model

### Critical

Use `critical` when evidence indicates directly exposed credential/private-key material and high-impact conditions such as production/admin scope, public/client distribution, material signing/decryption authority, or another broadly exploitable privileged exposure.

Do not use `critical` merely because a token matches a known format.

### High

Use `high` when likely credential material is exposed on a shared/reachable surface and misuse could provide meaningful unauthorized access.

### Medium

Use `medium` for material secret-handling defects without strong evidence of an immediately usable exposed credential, including unsafe plaintext persistence, long-lived shared credentials, insecure fallback, or dangerous privileged/untrusted secret-flow configuration.

### Low

Use `low` for limited-impact hygiene defects such as incomplete masking or examples that teach weak handling without likely usable credentials.

## Confidence model

### Confirmed

Use only when the artifact/evidence itself establishes secret semantics without external authentication, such as valid private-key material or explicit trusted evidence that the credential is real.

### Likely

Use when format plus context strongly indicates credential material: provider-specific token form in a real auth path, credential-bearing connection string, or authorization/session material in logs.

### Possible

Use when suspicious but ambiguous. Synthetic examples, placeholders, truncated/redacted strings, generic entropy matches, or ambiguous assignments normally remain `possible` unless corroborated.

Never authenticate merely to raise confidence.

## External validity evidence

Provider/user-supplied validity may be recorded separately as:

`active | inactive | unknown | not-supplied`

Validity affects remediation priority but does not erase evidence that a credential was exposed. An inactive secret may still warrant incident review for the period when it was active.

## Severity tie-breakers

When two severities are plausible, evaluate in order:

1. reachable exposure surface: public/client/shared-log/agent-output > restricted internal source > local-only;
2. privilege/authority: admin/signing/production > write > read > narrowly scoped test;
3. environment: production > shared non-production > isolated local test;
4. lifetime: reusable/long-lived > short-lived/ephemeral;
5. distribution breadth: history, artifacts, forks, logs, images, docs, or model/tool traces increase exposure breadth.

If authenticity is uncertain, lower confidence before lowering potential-impact severity solely for uncertainty.

## Evidence rules

Every finding requires exact/bounded location, narrow rule/category, redacted evidence, independent severity/confidence reasoning, and remediation linked to the defect.

A detector hit alone is insufficient for `confirmed` confidence or for final high/critical severity.

## Ordering and deduplication

Canonical final ordering:

`critical -> high -> medium -> low`, then location, rule, finding ID.

Merge overlapping detector hits for the same value/exposure defect; do not inflate counts with entropy + provider + assignment findings for one credential.

## Coverage semantics

Use the per-surface coverage states in `exposure-surfaces.md`. A partial or uninspected material surface cannot support a blanket clean conclusion.
