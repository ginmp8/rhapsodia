# Execution Visibility and Recovery

Use this reference when showing current execution state, resuming interrupted work, or diagnosing a lock or journal. The view is a **non-authoritative read-only projection**; `tasks.md`, `manifest.yaml`, registry state, MAGIA execution notes, validation evidence, command output, and the transaction journal retain their existing authority.

## Safe inspection

Run:

```bash
python scripts/summarize_execution_state.py <board-root> --spec-id <spec-id> --format markdown
```

The projection reports task checkboxes, execution-record status, check/evidence counts, traceability presence, canonical state-validation errors, lock ownership class, journal state, blockers, and the next safe action. It does not execute tests, recover transactions, mutate state, or certify completion.

## Recovery decisions

- `live_owner`: wait. Never take over the lock.
- `dead_owner` or a valid `prepared`/`committed` journal: run the existing recovery path, then repeat state validation.
- invalid metadata, unsafe paths, malformed journal, or missing required backups: stop mutation and inspect manually.
- clean lock/journal state with validation errors: repair evidence or state through the existing validated scripts before closure.
- clean state with no errors: continue only the selected bounded task and its planned proving check.

After recovery, rerun readiness or execution-state validation. Checks completed before an interrupted write may need to be repeated when repository or artifact drift is possible.
