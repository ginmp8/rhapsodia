# Integrity and Recovery

Use when an optimization depends on external source evidence or when packaging/delivery can mutate existing artifacts.

## Source evidence identity

When external files or repository content materially determine a hypothesis, benchmark interpretation, or acceptance decision, capture the exact bytes before analysis. Use the snapshot for the experiment and keep its identity separate from the live source.

```text
<PYTHON> scripts/snapshot_sources.py capture \
  --root <SOURCE_ROOT> \
  --path <RELATIVE_SOURCE> \
  --snapshot-dir <WORK>/source-bytes \
  --out <WORK>/source-manifest.json
```

Before acceptance:

```text
<PYTHON> scripts/snapshot_sources.py verify \
  --manifest <WORK>/source-manifest.json \
  --json <WORK>/source-verification.json
```

If the live source changed, either keep evaluating the frozen snapshot or invalidate and deliberately re-baseline the experiment. Do not mix before/after evidence from different source versions.

For pinned VCS evidence, prefer immutable revision/object reads over the working tree when the host supports them. Record repository identity, revision, path, and relevant range. Dirty files, moving refs, local replacement refs, or generated files must not silently redefine a pinned source.

## Output preflight

Before mutation, validate authored and resolved/canonical paths. Reject:

- package/report aliases, including hardlinks or symbolic-link aliases;
- outputs inside the frozen target;
- wrong filename/extension after path resolution;
- symbolic-link cycles;
- directories or special files where a normal file is required.

Preflight failure must leave all prior bytes unchanged.

## Last-known-good and recovery

Treat a package plus its receipt as one logical delivery transaction:

`stage -> validate -> hash -> backup existing -> commit package -> commit receipt -> cleanup backups`

If commit fails, restore the previous package/receipt. If rollback is incomplete, preserve exact recovery paths rather than deleting evidence. Never replace a last-known-good receipt with a failed-attempt receipt.

## Durable receipts

Success receipts must describe the exact committed archive and include, when applicable:

- `receipt_version`;
- `status` and `stage`;
- candidate hash;
- archive hash;
- validation/portability/reconciliation evidence;
- atomic replacement result;
- recovery information.

Persist success receipts atomically with the package. Failure receipts should remain available through stdout or a separately requested failure channel without overwriting a prior successful receipt.

## Acceptance implications

Do not claim final readiness when:

- material source identity changed without explicit re-baselining;
- package/report outputs alias each other or protected inputs;
- a failed attempt destroyed last-known-good bytes;
- rollback failed and recovery locations were discarded;
- the receipt does not correspond to the committed archive.
