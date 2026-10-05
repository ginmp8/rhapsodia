# Workflow Plan v2 Contract

## At a Glance

- **Purpose:** Preserve and validate historical `workflow-plan/v2` gated-convergence integrations without transferring new checkpoint-promotion ownership back into Adaptive Workflow Orchestration.
- **Load when:** An existing artifact explicitly uses `workflow-plan/v2` and its checkpoint/gate/promotion semantics must be interpreted or validated.
- **Decision impact:** Preserves v1 authority/budget/capability/evidence rules plus v2 checkpoint promotion invariants: only current passing required-gate evidence for the same candidate may promote a checkpoint, and repairs may invalidate prior evidence.
- **Do not load when:** Designing new checkpointed convergence; route that work to `checkpoint-convergence` and `convergence-plan/v1`.

## Contents

- Gated-convergence invariant
- Gates
- Checkpoints
- Promotion policy
- Candidate and evaluator freshness
- Version compatibility
- Reference-grounded convergence additions

`workflow-plan/v2` is an additive historical evolution of `workflow-plan/v1`. The v1 contract remains supported; new reference-grounded checkpoint promotion must not be created under v2.

## Gated-convergence invariant

A checkpoint is a bounded candidate increment. It may be repaired repeatedly within budget, but a downstream checkpoint must not begin until every dependency checkpoint is **promoted**. Promotion is valid only when every gate marked `required: true` has current passing evidence for the same candidate identity.

A controller must never reinterpret `fail`, `blocked`, `invalid`, `not-run`, reviewer disagreement, or missing evidence as a pass.

## Gates

Each gate declares:

- `kind`: `behavior | executable-proof | adversarial-review | perceptual | human-approval | custom`;
- whether it is required;
- isolation used by its evaluator;
- immutable evaluator identity for the attempt;
- optional semantic capability required to execute it;
- failure action;
- whether repair invalidates prior pass evidence and forces rerun;
- finite `max_attempts`.

`executable-proof` and `adversarial-review` require independent isolation (`fresh-context`, `workspace`, `process`, or `host-native`). `human-approval` uses `human` isolation. A gate `capability` is a semantic requirement, not a pinned external skill identity. The active verifier/reviewer resolves it through host-native capability/Agent Skill discovery inside its existing authority. A required gate that depends on an unavailable capability blocks progression; it never silently degrades to `not-run`.

`recapture` is reserved for perceptual/state-alignment failures where the compared states are invalid rather than semantically different.

## Checkpoints

Each checkpoint declares:

- a stable id and bounded objective;
- checkpoint dependencies;
- one producer stage that owns the candidate mutation/output;
- the gate ids that must evaluate that candidate;
- a local success predicate.

Checkpoint dependencies form a DAG. The number of checkpoints cannot exceed `budgets.max_checkpoints`.

At least one gate referenced by every checkpoint must be required. If a referenced gate uses `on_failure: repair`, `budgets.max_checkpoint_repairs` must be greater than zero.

## Promotion policy

For `gated-convergence`, all three policy values are hard invariants and therefore must be `true`:

- `requires_all_required_gates`;
- `next_checkpoint_requires_promoted_dependencies`;
- `accepted_feedback_only`.

`accepted_feedback_only` means the controller may carry forward explicit accepted feedback, decisions, or proven evidence with source/checkpoint identity. It must not turn model inference or an unaccepted reviewer suggestion into durable workflow memory.

## Candidate and evaluator freshness

Repair creates a new candidate identity. Any gate whose semantics could be affected by that repair must be rerun when `rerun_after_repair` is true. Never preserve a pass merely because the gate passed an earlier candidate.

A changed evaluator identity invalidates same-evaluator comparison claims and should be explicitly re-baselined.

## Version compatibility

- Existing `workflow-plan/v1` artifacts remain valid and continue to use `schemas/workflow-plan.schema.json`.
- New gated-convergence plans use `workflow-plan/v2` and `schemas/workflow-plan-v2.schema.json`.
- `scripts/validate_workflow_plan.py` auto-detects v1 versus v2 and preserves v1 behavior.

## Reference-grounded convergence additions

The following fields are additive and optional for backward compatibility:

- `evidence.freshness_policy`: `frozen-input`, `revalidate-before-mutation`, or `revalidate-before-promotion`.
- checkpoint `reference_scope`: non-empty reference identifiers/paths for the checkpoint.
- checkpoint `oracle_identity`: frozen acceptance/test/rubric identity derived before production.
- checkpoint `context_mode`: `fresh-context` or `reuse-current`.
- `promotion.gate_order_is_binding`: when present it must be `true`; the checkpoint `gate_ids` array becomes binding execution order.
- `promotion.materialize_promoted_checkpoint`: when `true`, runtime evidence must record an immutable promoted candidate/checkpoint identity before dependent work starts.
- `promotion.autonomy_policy`: `human-required`, `human-default`, or `policy-autonomous`.

When any checkpoint declares `reference_scope` or `oracle_identity`, every checkpoint must declare both and `evidence.reference_identity` must be present. `human-required` requires a required `human-approval` gate on every checkpoint. A live revalidation freshness policy requires `reference_identity`.

These fields do not authorize broader writes, new tools, or a different lifecycle owner.
