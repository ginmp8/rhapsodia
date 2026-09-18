# Ecosystem compatibility

Nomia, Mago, and Magia participate in coordinated exact ecosystem release `1.9.4`. Each package remains independently executable and carries local byte-equivalent copies of shared contracts. Runtime imports, script execution, or file reads from peer skill packages are forbidden.

## Policy

- Package versions must all equal `1.9.4`.
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
7. `scripts/validate_ecosystem_release.py` emits one passing attestation ledger bound to the same three roots and archives.

## Upgrade and rollback

Upgrade or roll back all three packages as one coordinated release. Do not partially deploy or reinterpret a prior package version as compatible.

## Canonical attestation command

Run the release-time coordinator from any one package copy with explicit candidate roots. The coordinator is release tooling only and does not create runtime peer coupling.

```bash
python -B scripts/validate_ecosystem_release.py \
  --mago <mago-root> --magia <magia-root> --nomia <nomia-root> \
  --output-dir <external-output>/coordinated-release \
  --json-output <external-output>/coordinated-release-ledger.json
```

The ledger fails when any mandatory local package/archive gate, compatibility check, routing/provenance/release-metadata check, positive harness, or negative harness is missing, skipped, timed out, or failed.
