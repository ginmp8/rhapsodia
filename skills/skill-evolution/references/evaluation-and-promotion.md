# Evaluation and Promotion

## Evaluation identity

Every comparable candidate carries the same frozen:

- evaluator id;
- scenario-set id;
- evaluation-policy id.

An identity mismatch makes peer dominance/Pareto claims invalid. Do not merge results across changed evaluators by convenience; restart/re-baseline when the deciding evidence contract changes.

## Evaluation ladder

Use caller-provided evidence through:

- L0 structural;
- L1 deterministic;
- L2 focused;
- L3 harness;
- L4 benchmark;
- L5 holdout.

The controller requests levels but never owns evaluator semantics. Record evidence type truthfully (`measured`, `supplied`, `derived`, `planned`, or `unknown`).

## Comparisons

Preserve three distinct comparisons:

- candidate vs direct parent for local attribution;
- candidate vs immutable baseline for cumulative regression;
- candidate vs peer only under comparable frozen evidence.

Use each objective's predeclared `min_delta` plus recorded uncertainty before declaring material superiority.

## Holdout

Use L5 only when the promotion claim requires it. If holdout feedback is exposed for repair, record `revealed-development`; it is no longer blind evidence. A later blind promotion claim needs fresh holdout evidence.

## Promotion boundary

Search output may recommend `promote-candidate`, `keep-baseline`, `gather-evidence`, or `no-single-winner`. The caller owns final change gate, final re-evaluation, freeze, packaging, installation, and canonical workflow-policy updates.
