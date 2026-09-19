# Self-Hosting Reproducibility Profile

Use this profile when the target skill can generate a modified candidate of itself. It adds reproducibility controls for self-hosting; it does not own broad improvement orchestration, hypothesis selection, or final product governance.

## Roles

- `controller`: immutable version executing the current generation;
- `baseline`: immutable target snapshot used for comparison;
- `candidate`: isolated mutated copy;
- `evaluator`: frozen acceptance assets outside the candidate mutation surface;
- `last_known_good`: previously accepted version preserved for recovery.

The controller may be logically equivalent to the baseline at generation start, but record both roles separately.

## Required controls

When `self_hosting.enabled = true`, record:

```text
generation_id
controller_identity
baseline_identity
candidate_identity or candidate_identity_pending
max_self_recursion_depth
controller_read_only
evaluator_outside_candidate_surface
promotion_external_to_candidate
last_known_good_identity
```

Default `max_self_recursion_depth = 1`. A candidate cannot recursively create and promote another generation before the current generation closes.

## Variability map additions

Map at least these self-hosting variance sources:

- mutable controller state;
- controller/candidate path aliasing;
- evaluator leakage into authoring or candidate execution;
- generation identity drift;
- promotion policy drift;
- recursive self-modification without a closed prior generation;
- last-known-good loss or rollback ambiguity;
- candidate receipt not matching promoted bytes.

Move objective controls downward where possible: path separation and hashes to scripts, generation/receipt shape to schemas, promotion invariants to validators/gates, and contextual judgment to rubrics.

## Generation acceptance invariants

A reproducibility claim for a self-hosted generation requires:

1. controller identity frozen before candidate mutation;
2. baseline and evaluator identities frozen before comparison;
3. controller/evaluator unchanged through final candidate evaluation;
4. candidate isolated from the controller tree;
5. generation ID stable across baseline/candidate evidence;
6. recursion limit respected;
7. promotion decision produced outside the candidate mutation surface;
8. accepted/published bytes identical to the frozen candidate identity;
9. last-known-good preserved until promotion commits successfully.

If behavioral evidence is unavailable, these controls support a **structurally reproducible self-hosting workflow**, not a claim that the candidate behavior improved.

## Bootstrap conformance

After promotion, verify that the new version still preserves the self-hosting contract, validators, protected evidence rules, and stop conditions. This may be a structural validation only. Do not automatically start another self-improvement generation as part of the same run.

## Stop conditions

Stop or downgrade claims when:

- controller and candidate share the same mutable tree;
- controller/evaluator identity changes after freeze;
- promotion can be authorized solely by candidate-mutated evidence;
- recursion exceeds the declared limit;
- last-known-good cannot be preserved for a mutating promotion;
- accepted artifact/receipt identity differs from the frozen candidate;
- the only route to a pass is weakening evaluator, safety, compatibility, or evidence gates.
