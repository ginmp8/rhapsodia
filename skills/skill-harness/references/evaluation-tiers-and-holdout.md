# Evaluation Tiers and Holdout Partitions

Use when a caller wants staged candidate evaluation or future multi-candidate search. This contract does not select winners; it defines scenario partitions and evidence visibility.

## Scenario tier

Scenarios may declare optional `evaluation_tier`:

- `L2-focused`: selected-hypothesis/touched-capability scenarios;
- `L3-harness`: broad regression, ambiguity, edge, and adversarial scenarios;
- `L5-holdout`: promotion-only independent/hidden scenarios.

`L0`/`L1` are deterministic package/test gates and normally do not need scenario entries. `L4` belongs to benchmark aggregation/comparison.

## Visibility

Scenarios/evaluator assets may declare:

- `candidate-visible`: legitimate task instructions/rubrics the candidate may read;
- `evaluator-only`: expected outcomes, hidden graders, or holdouts that must not be exposed to the evaluated candidate for a blind claim.

A holdout is not hidden merely because it lives in a different file. Blind claims require execution evidence showing evaluator-only assets were not visible.

## Partition identity

Record stable ids/hashes for the focused, harness, and holdout partitions. Baseline/parent/candidate comparisons must use the same partition identity for strict deltas.

## Promotion rule

Visible/focused suites can reject a bad candidate and support bounded conformance claims. When a candidate has been repeatedly optimized against the visible suite and the promotion claim is vulnerable to overfitting, require a frozen independent holdout or independent review before strong promotion claims.

Do not use holdout feedback to mutate the same candidate and still call that holdout unseen. Once revealed for repair, it becomes development evidence and a fresh holdout is needed for a blind final claim.
