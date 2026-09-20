# Transformation Records and Ablation

Use for bounded candidate mutation when the caller supplies a capability map, transformation id, parent identity, or asks for attribution/ablation. This reference is local to the experiment lifecycle; it does not turn Skill Improver into a global orchestrator.

## Transformation record

Before mutation, record:

- `transformation_id`;
- `change_intent`: repair, optimization, or experiment;
- `hypothesis_id` and evidence refs;
- parent/baseline candidate identity;
- affected capability ids/files;
- operation/mechanism summary;
- expected effect;
- evaluator/acceptance rule;
- rollback plan;
- dependencies/conflicts if known.

After evaluation, update only lifecycle/evidence fields: applied, accepted, rejected, or reverted plus result evidence. Do not rewrite the original hypothesis after seeing results.

## One causal batch by default

Prefer one semantic transformation per candidate. Multiple file edits are fine when they are inseparable implementation details of one mechanism. If independent transformations must be combined, record the batch as attribution-limited and state why independent testing is impractical.

## Ablation

Ablation is optional. Use it only when attribution changes a decision, for example:

- a multi-transformation candidate improved but one costly/risky transformation may be unnecessary;
- a transformation repeatedly correlates with strong outcomes but contribution is unclear;
- the caller needs evidence before reusing the transformation elsewhere.

For transformations `T1 + T2 + T3`, prefer targeted one-minus variants (`full`, `full-T2`) rather than exhaustive powerset search. All variants must use the same frozen evaluator/scenario identities and receive separate candidate/experiment identities.

Do not call absence-of-delta proof that a transformation is useless when the evaluator lacks sensitivity.

## Parent-child record

Every candidate decision should preserve:

- parent identity;
- candidate identity;
- transformation ids;
- evaluator/scenario identity;
- metric/gate delta;
- accepted/rejected/reverted decision;
- causal limitations.

This allows a caller to build an experiment registry without coupling this skill to a specific orchestrator.
