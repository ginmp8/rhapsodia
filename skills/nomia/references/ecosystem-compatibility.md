# Ecosystem compatibility

Nomia, Mago, and Magia participate in coordinated exact ecosystem release `1.7.0`. Each package remains independently executable and carries local byte-equivalent copies of shared contracts. Runtime imports, script execution, or file reads from peer skill packages are forbidden.

## Policy

- Package versions must all equal `1.7.0`.
- Mixed package versions are rejected before mutation or handoff consumption.
- Changelog entries are documentation and are not compatibility aliases or migration inputs.
- The handoff, priority, routing, compatibility, and provenance contracts must be byte-equivalent across packages.
- Multi-intent work resolves one current owner before mutation and sequences later owners through typed handoffs.
- Compatibility remains `coordinated-exact`; no implicit aliases or N/N-1 fallback are supported.

## Release gates

- Package-local archives remain individually distributable, but an ecosystem readiness claim requires all three package validators and the integrated flow harness.

1. Every local package validator and complete test suite passes.
2. Shared provenance hashes validate in every package.
3. The distributed routing corpus validates.
4. The positive ecosystem flow harness passes from all three copies.
5. The negative fail-closed harness passes from all three copies.
6. The strict ecosystem release gate accepts the coordinated candidates.

## Upgrade and rollback

Upgrade or roll back all three packages as one coordinated release. Do not partially deploy or reinterpret a prior package version as compatible.
