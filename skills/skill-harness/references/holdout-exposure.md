# Holdout Exposure Ledger

Use for promotion workflows where holdout status must remain auditable across candidate lineages. The holdout partition identity alone does not show whether its feedback later influenced mutation.

Validate with:

```text
<PYTHON> scripts/validate_holdout_exposure.py <LEDGER.json>
```

A final candidate may execute a holdout and still support a blind final claim if holdout-specific feedback is not revealed to the mutator and no later mutation uses that feedback. Once feedback is revealed or used for mutation, that lineage is no longer blind against the same holdout; use development evidence or a fresh independent holdout.

Harness records exposure status only. Survivor selection and promotion remain outside Harness ownership.
