# Candidate and Lineage Contract

Each candidate record must include:

- `candidate_id`;
- `role`: `canonical|evidence-driven|focused|novel-bounded|merge|backcross|repair|mutation|other`;
- `status`: `planned|generated|evaluating|active|rejected|finalist|terminal`;
- `candidate_identity` when generated;
- `parent_ids`;
- `base_parent_id` when generation needs one physical base;
- `donor_parent_ids` when applicable;
- `operator`;
- `transformation_ids`;
- `generation_receipt_ref`;
- `evaluation_ref`/level;
- hard-gate outcomes;
- metric values;
- novelty score/evidence when used;
- rejection/selection rationale.

## Parent semantics

`baseline` is the stable regression reference. A `parent` is a direct ancestor used for local attribution. They may be the same identity but must not be silently conflated.

For a multi-parent child, designate one `base_parent_id` whose bytes were mutated and list the others as donors. This makes the generation operation reproducible and keeps file ancestry distinct from semantic donor ancestry.

## Lineage invariants

- parent ids must already exist or refer to the immutable baseline pseudo-node;
- no candidate may parent itself;
- lineage must be acyclic;
- candidate ids are never reused;
- changing a candidate's bytes requires a new candidate identity/id;
- rejected candidates are retained in history;
- a final candidate's claimed transformations must match its generation receipt.
