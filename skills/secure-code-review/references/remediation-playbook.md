# Secret Handling Remediation Playbook

## Priority order

Use the least persistent credential mechanism that fits the platform:

1. workload, instance, or federated identity;
2. managed secret store with scoped access and rotation support;
3. deployment-time secret injection;
4. untracked developer-local configuration only when stronger platform mechanisms are unavailable.

Do not replace a hardcoded production secret with a different long-lived static secret and call the issue resolved.

## Immediate containment after likely exposure

When the material is likely real and exposed:

1. rotate or revoke it using the credential owner's supported process;
2. remove it from active code/config/logging paths;
3. search available neighboring surfaces for reuse or copies;
4. review privileges and reduce scope where possible;
5. determine whether repository history, CI logs, artifacts, tickets, screenshots, or documentation also contain it;
6. enable preventive detection or push protection where the hosting platform supports it.

Removal from the latest source file does not by itself invalidate copies that already exist elsewhere.

## Replacement patterns

### Runtime credentials

Prefer identity-based access. Otherwise load from a managed secret store or deployment-time injection. Required secrets should fail closed when absent; do not add secret fallback literals.

### Local development

Keep local secret files untracked. Example configuration files should contain non-secret synthetic markers only. Prefer developer identity or local secret-management facilities when practical.

### Connection strings

Separate credentials from committed endpoint/configuration data when the platform permits. Never emit full credential-bearing connection strings into logs or error messages.

### CI/CD and IaC

Use the platform's protected secret/identity mechanism. Avoid plaintext values in workflow YAML, Terraform variable files, generated plans, build arguments, or artifact metadata.

### Logging

Do not log authorization headers, cookies, bearer/session values, API keys, private keys, or full connection strings. Use field-level redaction. If operational correlation is needed, use a non-secret identifier or a one-way fingerprint designed for that purpose rather than a recoverable credential fragment.

## Repository/history cleanup

Treat history rewriting as a separate operational decision: it can reduce accidental rediscovery but may disrupt clones, forks, links, and collaboration. Rotation/revocation is the immediate security control; history cleanup does not substitute for it.

## Finding-specific remediation

| Finding | Preferred remediation |
|---|---|
| hardcoded credential | revoke/rotate if exposed; replace with identity or managed secret retrieval |
| private key material | replace the keypair; remove private material from repository/artifacts; restrict new key storage |
| credential in logs | revoke/rotate if usable; stop logging; redact existing accessible logs under retention/integrity policy |
| client-side credential | assume retrievability; remove privileged static secret; redesign around server-side or public-client auth model |
| unsafe fallback | remove fallback secret; fail closed or require explicit secure configuration |
| weak redaction | redact at structured field boundaries; test that raw credential bytes never reach sinks |

## Completion evidence

A remediation is stronger when the review can verify:

- active code/config no longer contains the literal;
- the credential was rotated/revoked when exposure was likely;
- least privilege was reviewed;
- logging/output paths are sanitized;
- preventive scanning exists for recurrence.

If those actions occur outside the available tools or evidence, mark them as recommended or user-supplied, not verified.
