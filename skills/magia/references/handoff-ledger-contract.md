# Handoff Ledger Contract

The ledger is local transport metadata, never a source of product, planning, execution, validation, or release authority. It records one `workflow_id` and append-only events for validated handoffs.

Allowed states are `created`, `accepted`, `consumed`, `superseded`, and `replayed`. Duplicate recording of the current state is idempotent. Invalid transitions, mismatched workflows, malformed handoffs, mutation of a superseded handoff, and mixed-version handoffs fail closed.

## Reproducibility and recovery

- `handoff_id` is content-derived; changing envelope content changes identity.
- Recording the same handoff in its current state is a safe rerun and appends no event.
- Before replacing an existing valid ledger, `commit_ledger` atomically preserves `<ledger>.last-good`.
- Recovery restores only a structurally valid last-known-good ledger and verifies the restored bytes.
- CLI mutation commands may emit machine-readable receipts; a receipt never transfers domain authority.
- Last-known-good is transport recovery evidence, not a competing source of product/planning/execution truth.

```text
python -B scripts/handoff_ledger.py init --ledger <ledger.json> --workflow-id <workflow-id> --receipt <receipt.json>
python -B scripts/handoff_ledger.py record --ledger <ledger.json> --handoff <handoff.json> --state created --receipt <receipt.json>
python -B scripts/handoff_ledger.py validate --ledger <ledger.json>
python -B scripts/handoff_ledger.py recover --ledger <ledger.json> --receipt <receipt.json>
```
