# Safe Cleanup Rules

Use these rules before any cleanup, simplification, consolidation, or deletion.

## Non-negotiable invariants

1. Preserve an immutable baseline or rollback source before mutation.
2. Build a deterministic inventory and trace direct plus transitive usage before calling a resource dead. When external/repository evidence decides classification, capture exact source bytes or an immutable pinned VCS object before analysis and verify that source identity before apply.
3. Classify every deletion candidate using the seven-state taxonomy.
4. `unknown` is fail-closed and is never automatically removed.
5. Prefer integrating useful resources over deleting them.
6. Preserve progressive-loading resources even when no script imports them.
7. Do not change domain behavior, activation, public contracts, evaluator baselines, or expected outputs without direct evidence and validation.
8. Dry-run the exact plan before apply when the apply helper is available.
9. Canonicalize paths and reject symlink/alias risk before mutation.
10. Preserve last-known-good bytes, validate after mutation, and roll back on failure.
11. Emit a durable machine-readable receipt for every apply attempt.
12. A second run of the same accepted plan must be idempotent.

## Protected resources

Never automatically edit, move, or delete:

- `.git/` and VCS metadata;
- secrets, credentials, keys, certificates, tokens, `.env` files, and private config;
- fixtures, golden files, expected outputs, snapshot baselines, benchmark reports, evaluator results, and generated evidence;
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
- state is `generated`, exact `duplicate`, or explicitly approved `obsolete`;
- non-empty evidence is recorded;
- fresh inventory agrees with `generated`/`duplicate` classification;
- `obsolete` has `approval: explicit` plus at least one strong evidence kind: `user-explicit`, `target-doc`, `replacement-verified`, `validator-proven`, or `migration-complete`;
- existing file hash matches `expected_sha256` immediately before deletion;
- no protected/progressive-loading/public compatibility role remains;
- rollback source exists;
- post-cleanup validation is available.

If any condition is uncertain, reject mutation rather than guessing.

## Cleanup plan contract

Machine-readable plans use:

```json
{
  "plan_version": 1,
  "actions": [
    {
      "action": "delete",
      "path": "dist/local-report.json",
      "classification": "generated",
      "evidence": [
        {"kind": "inventory", "value": "generated namespace; not reachable"}
      ],
      "expected_sha256": "<sha256>"
    }
  ]
}
```

For explicit obsolete cleanup also include:

```json
{
  "classification": "obsolete",
  "approval": "explicit",
  "evidence": [
    {"kind": "replacement-verified", "value": "references/new.md replaces references/old.md and all consumers were updated"}
  ]
}
```

The plan is declarative. It is not evidence that its own classification is correct; apply preflight rechecks the live target.

## Dry-run and apply

Dry-run and apply consume the same plan. Dry-run is default and must not mutate target bytes.

The apply helper rejects:

- unknown/used/integrable/blocked states unless an eligible resource was explicitly reclassified obsolete under the contract;
- missing evidence or expected file hash;
- classification mismatch;
- hash drift between plan and apply;
- symlink components, path escape, or noncanonical path spelling;
- receipt/work paths inside target;
- unsupported action types.

## Idempotency

After a successful delete, rerunning the same plan is a no-op for that path and records `already_absent`. The rerun still validates the current target before returning success.

Do not recreate deleted files merely to satisfy an old plan.

## Last-known-good and rollback

Before deleting any existing approved resource, copy the affected bytes to an external transaction directory. Record that directory in the receipt.

After mutation:

1. run post-cleanup structural validation;
2. if validation passes, commit the receipt with `status: pass`;
3. if validation fails, restore removed resources from last-known-good;
4. if restoration succeeds, record `status: rolled-back`;
5. if restoration is incomplete, record `status: recovery-required` and preserve all recovery paths/evidence.

Never report success from a stale last-good artifact after the candidate failed.

## Receipt contract

Receipts are durable JSON evidence and include at least:

- `receipt_version`;
- `status` and `stage`;
- target and plan identities;
- dry-run/apply mode;
- action results;
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
5. rerun inventory and validation.

## Rollback minimum for manual mutations

If a mutation cannot use `cleanup_apply.py`, record:

- files changed/removed;
- baseline identity and backup location;
- original and replacement paths;
- reason/evidence;
- exact validation command;
- deterministic rollback instruction.

Manual mutation must not weaken the safety guarantees simply because a helper cannot be used.
