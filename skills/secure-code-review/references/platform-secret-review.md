# Platform Secret Review

Load only for relevant platform surfaces. These checks stay scoped to credentials/secrets; route unrelated platform security issues elsewhere.

## CI/CD and GitHub Actions

Review secret **flows**, not only literals:

- identify privileged triggers/jobs and what credentials they receive;
- identify untrusted code, pull-request content, third-party actions, artifacts, or scripts that can execute in the same trust boundary;
- for GitHub Actions, treat `pull_request_target` and privileged `workflow_run` patterns as high-scrutiny when untrusted content can influence execution;
- review `GITHUB_TOKEN`/job permissions for least privilege;
- do not assume masking is complete when secrets are transformed, encoded, serialized, or embedded in structured data;
- inspect stdout/stderr, uploaded artifacts, caches, generated config, command arguments, and error paths when available.

A dangerous privileged/untrusted path may be a credential-exposure finding even when no literal credential is committed.

## Docker and container builds

- treat secret-like `ARG`/`ENV` use during builds as unsafe when the value can persist in image metadata/layers;
- prefer BuildKit secret mounts or SSH mounts for build-time secrets;
- inspect copied files, package-manager config, generated config, and image/layer contents when supplied;
- distinguish Dockerfile review from built-image proof.

## Kubernetes

- Base64 encoding in a `Secret` manifest is encoding, not encryption;
- committed Secret manifests can still expose real secret material;
- review whether encryption at rest is configured when cluster evidence is available;
- review RBAC for `get`, `list`, and `watch` access using least privilege when in scope;
- environment-variable delivery may broaden exposure through process/debug/crash surfaces; volume or identity-based patterns may be safer depending on the application.

## Terraform

- `sensitive = true` primarily redacts UI/CLI display; do not infer that the value is absent from plan/state;
- inspect state/plan artifacts when available and relevant;
- recognize Terraform ephemeral values (1.10+) and provider-supported write-only arguments (1.11+) as mechanisms that can avoid persistence;
- do not recommend write-only arguments unless the selected provider/resource supports them;
- review generated plan/state files as exposure surfaces, not just `.tf` source.

## Generic IaC and deployment systems

Review:

`source/config -> CI runner -> generated plan/artifact -> runtime injection -> logs/diagnostics`

A secret-store reference can still leak later through generated config, shell tracing, command arguments, logs, artifacts, or client-side packaging.
