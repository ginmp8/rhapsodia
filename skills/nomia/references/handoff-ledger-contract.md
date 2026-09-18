# Handoff Ledger Contract

The ledger is local transport metadata, never a source of product, planning, execution, validation, or release authority. It records one `workflow_id` and append-only events for validated handoffs.

Allowed states are `created`, `accepted`, `consumed`, `superseded`, and `replayed`. Duplicate recording of the current state is idempotent. Invalid transitions, mismatched workflows, malformed handoffs, and mutation of a superseded handoff fail closed.

```text
python -B scripts/handoff_ledger.py init --ledger <ledger.json> --workflow-id <workflow-id>
python -B scripts/handoff_ledger.py record --ledger <ledger.json> --handoff <handoff.json> --state created
python -B scripts/handoff_ledger.py validate --ledger <ledger.json>
```
