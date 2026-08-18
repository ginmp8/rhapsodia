# Lifecycle Status Projection

Nomia may render a read-only, non-authoritative view from validated handoffs and the authority-neutral ledger. The projection exposes current owner, pending handoff, blockers, source handoff IDs, and privacy classification without embedding raw evidence references. It never closes governance, rewrites planning, certifies execution, or becomes canonical state.

```text
python -B scripts/project_lifecycle_status.py --handoff <handoff.json> [--handoff <handoff.json>] [--ledger <ledger.json>] --output <status.json>
```
