# Mutation Transaction and Resume Contract

Use this contract for every Mago write step that can touch more than one canonical artifact. It protects planning state; it is not runtime execution evidence.


## Executable transaction runner

Use `scripts/mutation_transaction.py` for Mago-owned multi-artifact writes. The workspace must be outside the canonical package. A normal sequence is:

```bash
python scripts/mutation_transaction.py begin --package <package> --workspace <external-tx-dir> --write prd.md --write tasks.md
python scripts/mutation_transaction.py stage --workspace <external-tx-dir> --source-dir <prepared-files>
python scripts/mutation_transaction.py promote --workspace <external-tx-dir>
```

Use `resume` after an interruption that left the transaction `in_progress`. Use `rollback` after `rollback_required` or cancellation. The runner fingerprints all canonical package files and canonical manifest fields, records backups, rejects path traversal and symlinks, updates the manifest after every promoted file, detects unrelated drift, and verifies restored hashes before returning the manifest to `clean`. `--interrupt-after` and `--fail-after` exist for deterministic recovery testing and must not be used as production workflow shortcuts.

## Transaction boundary

One mutation step selects one internal mode and one package. Before writing:

1. record a unique transaction identifier outside generated views;
2. hash or otherwise fingerprint the inspected canonical inputs;
3. declare the complete package-relative write set;
4. stage changed files outside their canonical destinations;
5. validate the staged set with the same artifact and package gates used after promotion.

Promote staged files only after all stage validations pass. Use atomic replacement where the filesystem supports it. Registry identity is never replaced as part of a package-content transaction.

## Canonical manifest state

`manifest.yaml.mutation_state` is the readiness projection for the current mutation:

- `clean`: no staged or incomplete mutation remains; handoff may proceed if other gates pass;
- `in_progress`: the transaction, inspected digest, planned writes, completed writes, and checkpoint are recorded; handoff is blocked;
- `cancelled`: cancellation is explicit and recovery or cleanup remains; handoff is blocked;
- `rollback_required`: a partial promotion or failed post-write gate requires restoration; handoff is blocked.

Completed writes must be a subset of planned writes. A non-clean state must preserve `transaction_id`, `inspected_digest`, `planned_writes`, and `checkpoint`. Never mark the state clean merely to satisfy validation.

## Resume and drift

Resume only after recomputing the inspected-input digest and verifying that registry identity, dependencies, and every not-yet-promoted destination still match the recorded preconditions. On drift:

- stop the transaction;
- retain the staged files and checkpoint as non-canonical recovery evidence;
- classify the conflict;
- re-enter the appropriate Mago mode with refreshed evidence instead of overwriting concurrent work.

## Cancellation and rollback

Cancellation does not imply successful rollback. Mark `cancellation_requested: true`, stop new writes, and classify each planned destination as untouched, promoted, or restored. Set `rollback_required: true` whenever promoted state cannot be proven equivalent to the pre-transaction state.

Rollback restores only Mago-owned planning artifacts from recorded preconditions. It must not rewrite Magia evidence, generated projections, Nomia governance fields, or immutable registry identity.

## Validation and closure

Before returning to `clean`:

- verify all planned writes were either promoted and validated or explicitly abandoned before promotion;
- rerun artifact, package, repository, boundary, traceability, and triggered technical gates;
- verify no generated view became canonical;
- clear transient write sets only after the final checkpoint is recorded externally or in the caller-owned report.

A package validator must reject handoff/readiness while `mutation_state.status` is not `clean`.
