# Selection and Pareto Contract

## Eligibility first

Compare only candidates whose evaluation identity exactly matches the frozen evaluator/scenario/policy identity and whose required objective metrics are present. Report incompatible evidence separately; do not force a comparison.

Then apply hard gates. A failed/blocked/not-run required hard gate cannot be offset by quality, novelty, token, or cost gains.

## Noise-aware dominance

Each objective declares a direction and `min_delta`. Metrics may be a number or `{value, uncertainty}`. For pairwise comparison, treat the required material margin as:

`min_delta + uncertainty(A) + uncertainty(B)`

Candidate A dominates B only when A is not materially worse on every comparable objective and is materially better on at least one. This prevents tiny/noisy differences from becoming fake wins.

Do not invent a scalar overall score unless the weighting policy was frozen before results were observed.

## Canonical preservation

Roles listed in `preserve_roles` remain available as active references when eligible, even if dominated, subject to active-capacity limits. This keeps the canonical comparator available for later backcross and cumulative comparison.

## Derived novelty

Do not accept an arbitrary model-authored novelty score. Under `transformation-jaccard-v1`, derive diversity from transformation-set Jaccard distance. When the frontier exceeds capacity, greedily preserve max-min transformation diversity, then prefer lower evaluation uncertainty, then stable candidate id.

Novelty never rescues a hard-gate failure or incompatible evaluation evidence.
