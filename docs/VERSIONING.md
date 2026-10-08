# Versioning

RhapsodIA distinguishes **package release version** from **internal semantic contract version**.

- Package/marketplace/plugin metadata for this release is `0.8.0`.
- Internal contracts use independent semantic identities such as `agent-system-contract/v4`, `dynamic-workflow-plan/v1`, `convergence-plan/v1`, `workflow-plan/v1`, and `workflow-plan/v2`.
- Do not global-search/replace internal contract versions merely to match the package release.
- Release validation must fail when known package metadata diverges from `marketplace/catalog.json`.
