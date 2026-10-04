# Nondeterminism and Stability

Treat retries as evidence collection, not a way to search for a green result.

## Freeze controls before execution

Use `nondeterminism` to state the relevant controls:

- `mode`: `deterministic`, `controlled`, or `probabilistic`;
- `repetitions`: minimum observations required for strong proof;
- seed policy;
- input/order policy;
- clock/time policy;
- scheduler policy;
- `statistical_rule` for probabilistic/statistical claims.

Use `not-applicable` only when that surface cannot materially affect the claim.

## Stability rule

For the same frozen spec/candidate/evaluator, observing both `expected-observation` and `oracle-rejection` is evidence of instability. Report `inconclusive`/`unstable-observation`; do not choose the last or most convenient result.

Harness/environment errors are not semantic outcomes. They may justify retry within the finite attempt budget if the spec permits it, but they do not themselves prove or reject the claim.

## Probabilistic oracles

Predeclare the statistical decision rule and repetitions before candidate-specific results are inspected. The bundled verifier checks identity, repetition count, and contract shape; it does not evaluate arbitrary domain statistics. Preserve the statistic calculation or independent evaluator evidence separately.
