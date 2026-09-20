# Search Model

## Lifecycle

Use evidence-guided champion-challenger search:

`freeze -> validate -> seed -> generate -> cheap-evaluate -> validate-state -> select -> recombine -> validate-state -> checkpoint -> stop -> finalists`

Search semantic transformations and candidate strategies; never mutate target files directly.

## Contract generation

New searches use search-contract **v3** and search-state **v3**. Do not silently reinterpret v1/v2 artifacts. For an old run, either finish it with the old controller or explicitly re-baseline into v3 with new frozen identities. A re-baseline is a new search identity, not a continuation.

Freeze these before candidate mutation:

- target/baseline identity;
- capability-map, hypothesis-pool, transformation-registry, and evaluation-plan identities;
- evaluator, scenario-set, and evaluation-policy identities;
- hard gates and objective directions/minimum deltas;
- mutation/evaluation interface identities;
- budget and selection policy.

## Default population

Seed up to four evidence-supported roles:

- `canonical`;
- `evidence-driven`;
- `focused`;
- `novel-bounded`.

Do not invent transformations to fill the population. Keep at most four active candidates, normally evaluate 8-12 total, and treat 20 as a hard ceiling.

## Search rounds

A round may request 1-3 children. Validate every request before mutation. Reject duplicates, dependency gaps, declared conflicts, capability-invariant violations, unknown transformations, or budget overflow before spending mutation/evaluation cost.

History is append-only. Rejected candidates and skipped requests remain negative evidence.

## Deterministic stagnation

Treat a completed round as stagnant only when both are true relative to the previous checkpoint:

1. the Pareto archive is unchanged; and
2. the round introduces no new transformation-set signature.

Use `scripts/checkpoint_search_state.py`; do not increment/reset stagnation by prose judgment. Stop when the configured consecutive-stagnation threshold is reached.

## Cost control

Escalate evaluation only after lower required levels pass. L4/L5 are not default development loops. L5 remains promotion-oriented and holdout blindness must be preserved.
