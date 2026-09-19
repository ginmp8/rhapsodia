# Recovery, Last-Known-Good, and Receipts

## Recovery invariant

A failed repair or package attempt must not destroy the last-known-good state or its evidence.

## Baseline and candidate

- Keep baseline copy/VCS identity outside the target mutation scope.
- Keep evaluator manifests and before/after reports outside the target.
- Prefer staging when the host supports it; otherwise ensure a verified rollback source exists before mutation.
- Never call a state last-known-good merely because it is older. It must have passed the declared gates at the time it was accepted.

## Rollback trigger

Rollback or restore from last-known-good when a repair introduces a blocker/high regression, evaluator integrity fails, candidate/report identity mismatches, package validation fails, or atomic commit cannot complete.

If rollback is incomplete, preserve both recovery backup and failed candidate paths. Do not erase evidence to make the workspace look clean.

## Receipt minimum

A durable consistency receipt should contain:

- receipt version;
- target/mode/status;
- baseline inventory identity;
- final candidate inventory identity;
- added/removed/changed file list;
- final report hash/path;
- evaluator manifest hash plus verification result;
- last-known-good identity/path when available;
- explicit claim boundary.

Receipt outputs must live outside the frozen target package. `scripts/create_consistency_receipt.py` rejects candidate/report identity drift.
