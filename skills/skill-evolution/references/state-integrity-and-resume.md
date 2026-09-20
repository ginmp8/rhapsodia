# State Integrity and Resume

Validate search-state v4 before survivor selection and again before every checkpoint. Use an external checkpoint receipt for every completed search round. The state file remains ordinary JSON; the receipt binds the exact canonical JSON bytes by SHA-256 without creating a self-referential hash field.

## Create checkpoint

```text
<PYTHON> scripts/checkpoint_search_state.py create \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json> \
  --out <ROUND_RECEIPT.json> \
  [--previous-receipt <PREVIOUS_RECEIPT.json>]
```

The receipt records contract/state hashes, previous-receipt hash, round, candidate count, Pareto archive, transformation-set signatures, search status, and the deterministic stagnation result.

## Resume

Before `resume`, verify the last checkpoint:

```text
<PYTHON> scripts/checkpoint_search_state.py verify \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json> \
  --receipt <ROUND_RECEIPT.json> \
  [--previous-receipt <PREVIOUS_RECEIPT.json>]
```

Do not continue when contract/state hash, previous-receipt link, round progression, search id, or stagnation counter mismatches. Reconstruct from the last known-good checkpoint or explicitly start a new search identity.

## Stagnation contract

For round N > 0, the checkpoint derives stagnation from the previous receipt. The current state's `stagnant_rounds` must equal the derived counter. This prevents the model from extending or resetting search budget by judgment after seeing results.
