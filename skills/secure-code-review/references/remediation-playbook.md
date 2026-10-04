# Secret Handling Remediation Playbook

## Preferred replacement order

Use the least persistent credential mechanism that satisfies the platform:

1. workload/instance/managed identity;
2. federated identity or OIDC;
3. dynamically issued short-lived credentials;
4. managed secret store with scoped access and rotation;
5. deployment/runtime injection;
6. developer-local untracked configuration only when stronger mechanisms do not fit.

Do not replace a hardcoded production secret with a different long-lived static secret and call the issue resolved.

Environment variables are an injection mechanism, not a universal security boundary. Review process inheritance, debug/crash output, container metadata, command construction, and child processes before treating environment delivery as sufficient.

## Immediate containment after likely exposure

1. rotate or revoke the credential using the owner/provider process;
2. stop the active exposure path;
3. search available neighboring surfaces for copies or reuse;
4. review privileges and reduce scope;
5. investigate relevant logs/access history when available and appropriate;
6. prevent recurrence with scanning/push protection/CI guards where supported;
7. consider history/artifact cleanup after containment.

Rotation/revocation is the primary control. Repository history rewriting is secondary and can disrupt clones, forks, links, and collaboration; it does not remove copies from other users' clones/forks.

## External validity

If trusted provider/user evidence says a discovered secret is `active`, prioritize containment. If `inactive`, still assess historical exposure. `unknown` is not proof of safety.

This skill never performs its own authentication attempt with discovered material.

## Replacement patterns

### Runtime credentials

Prefer workload/federated identity. Otherwise use managed retrieval or short-lived issuance. Required secrets should fail closed when absent; do not add literal fallback secrets.

### Local development

Keep local secret files untracked. Examples must use clearly synthetic placeholders. Prefer developer identity/local secret-management facilities where practical.

### CI/CD

Use protected identity/secret mechanisms and least privilege. Keep privileged credentials away from untrusted code paths. Avoid exposing secrets through command lines, debug output, generated artifacts, or transformed values that masking will not reliably catch.

### Docker builds

Do not pass build secrets through `ARG`/`ENV` when they may persist. Prefer BuildKit secret mounts or SSH mounts, and inspect built images/layers when supplied.

### Kubernetes

Do not treat Base64 as encryption. Prefer least-privilege Secret access and cluster encryption-at-rest controls when cluster evidence is in scope. Review whether environment-variable injection expands process/log exposure.

### Terraform

Do not treat `sensitive = true` as proof that data is absent from plan/state. Prefer ephemeral values and supported write-only arguments when persistence is unnecessary; protect state/plan storage and inspect them when available.

### Logging and agent output

Do not log authorization headers, cookies, bearer/session values, API keys, private keys, connection strings, or secret-bearing structured objects. Redact at structured-field boundaries before serialization. Account for transformed/derived credentials and agent-visible stdout/stderr/tool traces.

## Completion evidence

A remediation is stronger when evidence verifies:

- active code/config/artifact no longer contains or emits the credential;
- exposed credentials were rotated/revoked when needed;
- least privilege was reviewed;
- output/log/tool paths are sanitized;
- recurrence prevention exists.

Actions outside available evidence remain `recommended` or `user-supplied`, not `verified`.
