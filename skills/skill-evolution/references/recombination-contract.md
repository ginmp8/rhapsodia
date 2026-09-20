# Recombination Contract

Recombine semantic transformations, not raw diffs.

## Operators

- `transformation-merge`: combine complementary survivor transformations.
- `backcross`: apply useful donor transformations on the canonical base to recover canonical characteristics.
- `repair-crossover`: add a registry transformation explicitly mapped to a recorded non-blocking deficit.
- `bounded-mutation`: add/remove/replace one evidence-backed transformation or bounded strategy parameter.

## Mandatory preflight

Before emitting any candidate request:

1. resolve every transformation id against the frozen registry;
2. compute dependency closure and require all dependencies;
3. reject declared conflicts;
4. reject transformations declaring violation of frozen capability invariants;
5. reject rejected/deprecated transformations;
6. derive expected capability effects from registry entries;
7. reject duplicate `(base_parent, transformation-set)` strategies;
8. enforce candidate budget;
9. preserve holdout blindness and never use hidden evaluator details as mutation input.

Run `scripts/validate_candidate_request.py` on model-authored requests. `scripts/plan_recombination.py` applies the same controls for deterministic merge/backcross planning.

## Candidate request v2

```json
{
  "request_version": 2,
  "candidate_id": "C007",
  "operator": "transformation-merge",
  "base_parent_id": "C003",
  "donor_parent_ids": ["C005"],
  "transformation_ids": ["T002", "T003"],
  "expected_capability_effects": ["activation", "lineage-integrity"],
  "reason": "combine complementary validated transformations",
  "request_signature": "sha256-of-base-plus-transformation-set"
}
```
