# Evaluation and Promotion

## Ladder

Use caller-provided evidence through:

- L0 structural;
- L1 deterministic;
- L2 focused;
- L3 harness;
- L4 benchmark;
- L5 holdout.

A search controller may request evaluation levels; it does not own evaluator semantics.

## Comparisons

Preserve:

- candidate vs parent for local transformation attribution;
- candidate vs stable baseline for cumulative regression;
- candidate vs peer candidates for non-dominance only when evaluator identities are comparable.

## Holdout

Use holdout only when the promotion claim justifies it. If holdout feedback is revealed for repair, mark it development evidence and require a fresh holdout before any later blind claim.

## Promotion boundary

Search output may recommend:

- `promote-candidate`;
- `keep-baseline`;
- `gather-evidence`;
- `no-single-winner`.

The caller owns final change gate, freeze, package, install, and any canonical workflow-policy update.
