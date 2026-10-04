# Supply-Chain Security

Use for `dependency-risk-review` whenever risk extends beyond a package/version/CVE lookup.

## Evidence layers

Review the smallest applicable chain:

`source -> build/workflow -> package/artifact -> model/prompt/skill/tool/plugin/MCP server -> runtime configuration/deployment`

For each material component, record identity and provenance evidence when available. A hash or signature proves identity/integrity only within its trust assumptions; it does not prove safety.

## Source/build/workflow controls

Inspect where relevant:

- source origin, repository/revision identity, protected release path, and review requirements;
- build provenance/attestations and whether produced artifacts can be tied to reviewed source and builder identity;
- mutable tags/branches versus immutable commit/digest pinning for privileged workflow dependencies;
- package-manager lifecycle hooks, install-from-url/git, registry overrides, mirrors, and unsigned/unverified downloads;
- CI/CD token permissions and whether workflows use least privilege;
- privileged workflows triggered by or checking out untrusted pull-request/fork content;
- secrets exposed to untrusted build steps;
- model/tool/plugin/MCP/skill origin and update channel when those artifacts carry executable or authority-bearing behavior.

Do not convert absence of SLSA, SBOM, signature, or attestation into a vulnerability by itself. Classify the concrete assurance gap and its impact on provenance/verification.

## Current vulnerability claims

Keep the existing exact-dependency evidence rule: CVE applicability requires resolved package/version/ecosystem identity plus current scanner or authoritative advisory evidence and relevant conditions. Supply-chain posture findings and CVE findings are separate.

## Portable inventory

When a supplied SBOM/ML-BOM/agent BOM exists, use it as evidence only after binding it to the target/revision/runtime. Portable formats may improve coverage but are optional; core review must still work without a vendor-specific BOM tool.
