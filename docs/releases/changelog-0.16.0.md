# RhapsodIA distribution changelog — 0.16.0

## Added

- Six independently activatable Spec Conformance Auditor Skill packages (one coordinator and five stage adapters).
- Frozen requirement/source identity, bounded reachability and causal checks, executable-proof distinction and fork parity workflows.
- Standard-library report/receipt validators, deterministic routing helper, activation fixtures and source attribution notes.
- Portable integration and coordinator regression tests.
- Branch Reconciliation v0.1.0, a reusable Git three-way content integration skill with full-tree preservation checks, reviewed conflict resolutions, single-parent commits and non-force delivery guidance.
- Real-Git synthetic reconciliation scenarios and cross-platform CI validation.

## Distribution

- 69 Skills and eight native agents; previously 62 Skills and eight agents.
- Host marketplace/plugin versions aligned to 0.16.0.
- Pinned agent/source manifests and cross-platform CI expectations updated.

## Preserved

- Existing specialist Skill implementations, agent responsibilities, semantic contracts and previous release history.
- The coordinator's `spec-audit/v1` contract and read-only authority.
- Local fallback when optional external specialists are unavailable.
- Default read-only planning, explicitly authorized local Git changes, and no automatic fetch, push, merge commit, or release publication.

See [release notes](0.16.0.md) and the [changelog](../../CHANGELOG.md).
