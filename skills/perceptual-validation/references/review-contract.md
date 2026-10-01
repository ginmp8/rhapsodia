# Perceptual Review Contract

## Request

`perceptual-review-request/v1` binds:

- reference and candidate artifact identities;
- artifact kind;
- intended reference/candidate state;
- declared comparison scope;
- rubric categories;
- evaluator identity;
- required review capability.

State descriptions must be specific enough to identify incompatible states such as loading vs loaded, error vs success, expanded vs collapsed, or different data fixtures.

## Result

`perceptual-review-result/v1` binds the same artifact/evaluator identities and adds:

- `state_alignment`: `matched | mismatched | unknown`;
- `verdict`: `pass | fail | invalid | blocked | inconclusive`;
- findings with region, category, difference, severity, confidence;
- whether review actually executed.

Hard relations:

- `pass|fail` require `state_alignment=matched` and `review_executed=true`;
- `invalid` requires `state_alignment=mismatched`;
- `blocked` or `inconclusive` must not be promoted as pass;
- `fail` requires at least one finding;
- `pass` cannot contain a blocking/high finding.
