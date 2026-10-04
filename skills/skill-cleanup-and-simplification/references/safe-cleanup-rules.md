# Safe Cleanup Rules

Use these rules before any cleanup, simplification, consolidation, or deletion.

## Non-negotiable invariants

1. Preserve an immutable baseline or rollback source before mutation.
2. Build a deterministic inventory and trace direct plus transitive usage from the exact recorded root registry before calling a resource dead.
3. When external/repository evidence decides classification, capture exact source bytes or an immutable pinned VCS object before analysis and verify identity before apply.
4. Classify every deletion candidate using the seven-state taxonomy.
5. `unknown` is fail-closed and is never automatically removed.
6. Generated-like directory names are signals only; they never authorize deletion by themselves.
7. Prefer integrating useful resources over deleting them.
8. Preserve progressive-loading resources, evaluators/tests, contracts, and public compatibility surfaces unless a validated replacement exists.
9. Do not change domain behavior, activation, public contracts, evaluator baselines, or expected outputs without direct evidence and validation.
10. Dry-run the exact plan before apply when the apply helper is available.
11. Canonicalize paths and reject symlink/alias risk before mutation.
12. Preserve last-known-good bytes, validate after mutation, and roll back on failure.
13. Emit a durable machine-readable receipt for every apply attempt.
14. A second run of the same accepted plan must be idempotent.

## Protected resources

Never automatically edit, move, or delete:

- `.git/` and VCS metadata;
- secrets, credentials, keys, certificates, tokens, `.env` files, and private config;
- fixtures, evals/tests, golden files, expected outputs, snapshot baselines, public contracts, benchmark reports, evaluator results, and generated evidence;
- existing `*.zip`, `*.tar`, `*.tgz`, `*.7z`, and package archives;
- user-declared read-only files;
- unrelated files outside target scope;
- symlinks or paths whose canonical destination cannot be proven safe.

Protection wins over cleanup convenience.

## Canonical deletion eligibility

A deletion candidate must satisfy all applicable conditions:

- canonical relative path with no absolute, `.` or `..` segments;
- every existing path component is non-symlinked;
- resolved destination stays inside target;
- state is exact `duplicate`, strongly evidenced `generated`, or explicitly approved `obsolete`;
- non-empty evidence is recorded;
- fresh inventory uses the same root registry as planning;
- weak generated-like namespaces require `approval: explicit` plus one corroborating evidence kind: `user-explicit-generated`, `target-doc`, `generator-command`, `manifest-generated`, or `reproducible-generated`;
- `obsolete` requires `approval: explicit` plus `user-explicit`, `target-doc`, `replacement-verified`, `validator-proven`, or `migration-complete`;
- existing file hash matches `expected_sha256` immediately before deletion;
- no protected/progressive-loading/public compatibility role remains;
- rollback source exists;
- required structural and explicitly approved target validation is available.

If any condition is uncertain, reject mutation rather than guessing.

## Cleanup plan v2

Plan v1 remains readable for backward compatibility. Prefer v2 for new work because it can freeze declared roots, checkpoints, and explicit target validation commands.

```json
{
  "plan_version": 2,
  "roots": [
    {"kind": "runtime-root", "path": "runtime/entry.json"}
  ],
  "validation_commands": [
    {
      "name": "target-regressions",
      "approved": true,
      "argv": ["<PYTHON>", "scripts/run_regressions.py"],
      "timeout_seconds": 120
    }
  ],
  "actions": [
    {
      "action": "delete",
      "path": "__pycache__/helper.pyc",
      "classification": "generated",
      "checkpoint": "cache-residue",
      "evidence": [
        {"kind": "inventory", "value": "strong bytecode/cache evidence; not reachable"}
      ],
      "expected_sha256": "<sha256>"
    }
  ]
}
```

For a weak generated-like namespace, use explicit corroboration rather than path naming:

```json
{
  "action": "delete",
  "path": "dist/local-report.json",
  "classification": "generated",
  "approval": "explicit",
  "evidence": [
    {"kind": "generator-command", "value": "documented command reproduces this exact artifact"}
  ],
  "expected_sha256": "<sha256>"
}
```

The plan is declarative. It is not evidence that its own classification is correct; apply preflight rechecks the live target and root registry.

## Validation command safety

`validation_commands` are optional and must come from the operator/orchestrator, never be auto-discovered from untrusted target content during apply.

Each command must:

- use an argv array, never a shell string;
- set `approved: true` explicitly;
- run with the target as working directory;
- use a bounded timeout;
- be safe for the target trust class and environment.

The apply helper executes them only after internal structural validation. Any non-zero exit, timeout, or launch error triggers whole-transaction rollback. If executing target code is unsafe or unauthorized, omit these commands and run target-owned behavioral validation outside the transaction; report it separately as `not-run`/blocked until executed.

## Dry-run and apply

Dry-run and apply consume the same plan. Dry-run is default and must not mutate target bytes.

The apply helper rejects:

- `used`, `blocked`, or other fail-closed states without an allowed explicit reclassification;
- weak generated-like candidates without corroborating evidence;
- missing evidence or expected file hash;
- classification mismatch;
- hash drift between plan and apply;
- symlink components, path escape, or noncanonical path spelling;
- receipt/work paths inside target;
- missing declared roots;
- unsupported action types or validation command shapes.

## Checkpoints and transaction semantics

Actions may carry a `checkpoint` name. The apply helper validates package structure after each checkpoint to localize failures, but all checkpoints remain one transaction: failure at any checkpoint or final validation rolls back every action already applied in that transaction.

This provides small verification steps without leaving a half-cleaned candidate committed.

## Idempotency

After a successful delete, rerunning the same plan is a no-op for that path and records `already_absent`. The rerun still validates the current target before returning success. Do not recreate deleted files merely to satisfy an old plan.

## Last-known-good and rollback

Before deleting any existing approved resource, copy the affected bytes to an external transaction directory. Record that directory in the receipt.

After mutation:

1. run checkpoint structural validation;
2. run final structural validation;
3. run explicitly approved target validation commands when supplied;
4. if all required validation passes, commit the receipt with `status: pass`;
5. if validation fails, restore every removed resource from last-known-good;
6. if restoration succeeds, record `status: rolled-back`;
7. if restoration is incomplete, record `status: recovery-required` and preserve all recovery paths/evidence.

Never report success from a stale last-good artifact after the candidate failed.

## Receipt contract

Receipts are durable JSON evidence and include at least:

- `receipt_version`;
- `status` and `stage`;
- target and plan identities;
- dry-run/apply mode;
- action and checkpoint results;
- explicit validation command results when supplied;
- stable diagnostic codes and evidence;
- before/after or rollback tree identities when available;
- last-known-good path and recovery results when mutation occurred.

Write receipts atomically outside target and only after the described stage is known.

## Consolidation rules

Treat duplication as real only when content serves the same purpose and no unique semantic constraints remain. Similar text can be intentional across modes.

When consolidating:

1. choose the clearest canonical source;
2. preserve unique semantics;
3. update every consumer, local link, workflow reference, template instruction, and script path;
4. retain compatibility aliases only when externally required;
5. rerun inventory, activation-sensitive checks when metadata changed, and final validation.

## Rollback minimum for manual mutations

If a mutation cannot use `scripts/cleanup_apply.py`, record:

- files changed/removed;
- baseline identity and backup location;
- original and replacement paths;
- reason/evidence;
- exact validation command;
- deterministic rollback instruction.

Manual mutation must not weaken the safety guarantees simply because a helper cannot be used.
