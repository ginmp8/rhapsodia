# Candidate and Lineage Contract

## Candidate record

Use search-state v4. Each generated candidate records:

- unique `candidate_id`, role, lifecycle status, and immutable `candidate_identity`;
- `parent_ids`, one physical `base_parent_id`, and optional donor parents;
- operator and transformation ids;
- derived/declared expected capability effects;
- an identity-bound `generation_receipt` summary;
- an `evaluation` record with frozen evaluator identity, level, evidence type, gates, metrics, uncertainty, deficits, and holdout status.

`planned` candidates may omit generated-byte evidence. `generated` and later states require candidate identity and generation receipt. `active`/`finalist` candidates require a complete comparable evaluation.

## Parent semantics

The baseline is the immutable cumulative regression reference. A parent is a direct ancestor. For multi-parent children, exactly one `base_parent_id` identifies the bytes mutated; donors contribute semantic transformations only.

Parents must already exist earlier in append-only state or be the baseline pseudo-node. Donors must be parents and cannot equal the base parent.

## Receipt invariants

The generation receipt summary must match the candidate on:

- candidate identity;
- base parent;
- donor set;
- operator;
- transformation set.

This validates internal provenance consistency. It does not independently prove an external mutation service told the truth; callers should bind `receipt_identity` to their actual mutation receipt.

## Lineage and strategy invariants

- no self-parenting or cycles;
- no candidate-id reuse;
- new bytes require a new candidate id/identity;
- transformation ids must exist in the frozen registry;
- all dependencies must be present;
- declared conflicts cannot coexist;
- transformations that violate frozen capability invariants cannot enter a valid candidate;
- the same physical base plus the same transformation set cannot be generated twice as separate search strategies;
- rejected candidates remain in history.
