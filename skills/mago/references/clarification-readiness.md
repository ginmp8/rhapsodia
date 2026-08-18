# Clarification Readiness Contract

Use contract version 2 for new or materially refined `standard` and `governed` planning when assumptions, blockers, or open questions affect handoff. Governed packages entering `execute`, `review`, or `done` must carry `clarification_contract: 2` in `notes.md`.

## Stable records

Use `ASSUMPTION-NNN`, `BLOCKER-NNN`, and `QUESTION-NNN` headings. Every record declares:

- `Status` appropriate to its kind;
- `Severity`: `low`, `medium`, `high`, or `critical`;
- concrete `Evidence`;
- accountable `Owner` role;
- observable `Resolution condition`;
- `Resolution evidence` whenever closed.

When several records are open, rank and batch them through [clarification prioritization](clarification-prioritization.md). Handoff fails for any open blocker and for open high/critical assumptions or questions. Lower-severity open records may continue only when visible in the handoff output and accepted by the downstream planning boundary; Mago still does not accept business or security risk.

## Validation

```bash
python -B scripts/validate_clarification_readiness.py <package>/notes.md --require-v2
python -B scripts/validate_clarification_readiness.py <package>/notes.md --require-v2 --handoff
```

The validator checks structure and handoff readiness. It does not resolve questions, prove evidence, assign governance authority, or convert an assumption into fact.
