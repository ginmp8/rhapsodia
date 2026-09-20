# Selection and Pareto Contract

## Validate state before selection

Survivor selection operates only on a search-state v3 document that passes `scripts/validate_search_state.py`. The selector validates the state defensively as well; invalid lineage, receipts, candidate identity, evaluation references, or state version return `status=fail` and no survivors.

## Eligibility first

Compare only candidates whose evaluation identity exactly matches the frozen evaluator/scenario/policy identity and whose required objective metrics are present. Report incompatible evidence separately; do not force a comparison.

Selection eligibility is frozen by search-contract v3:

- `measured` and `supplied` evidence may be selected;
- `planned`, `unknown`, and unproven `derived` evidence remain recordable but are not survivor-selection evidence;
- `blind-fail` is a hard elimination from selection;
- `revealed-development` may inform development but is not a blind-promotion claim.

Then apply hard gates. A failed/blocked/not-run required hard gate cannot be offset by quality, novelty, token, or cost gains.

## Comparable evaluation levels

Under `comparison_level_policy=same-level`, Pareto dominance is computed only between candidates evaluated at the same ladder level. L2 evidence cannot dominate L4 evidence, and L4 evidence cannot be treated as numerically equivalent to L2 merely because metric names match. Candidates at different levels may remain active for further evaluation, but their metric values are not a peer-dominance comparison.

## Noise-aware dominance

Each objective declares a direction and `min_delta`. Metrics may be a number or `{value, uncertainty}`. For pairwise comparison, treat the required material margin as:

`min_delta + uncertainty(A) + uncertainty(B)`

Candidate A dominates B only when A is not materially worse on every comparable objective and is materially better on at least one. This prevents tiny/noisy differences from becoming fake wins.

Do not invent a scalar overall score unless the weighting policy was frozen before results were observed.

## Canonical preservation

Roles listed in `preserve_roles` remain available as active references when eligible, even if dominated, subject to active-capacity limits. This keeps the canonical comparator available for later backcross and cumulative comparison.

## Derived novelty

Do not accept an arbitrary model-authored novelty score. Under `transformation-jaccard-v1`, derive diversity from transformation-set Jaccard distance. When the frontier exceeds capacity, greedily preserve max-min transformation diversity, then prefer lower evaluation uncertainty, then stable candidate id.

Novelty never rescues an invalid state, ineligible evidence, a blind holdout failure, a hard-gate failure, or incompatible evaluation evidence.
