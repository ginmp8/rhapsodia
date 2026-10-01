# Workflow Plan v2 Contract

`workflow-plan/v2` is an additive evolution of `workflow-plan/v1`. It preserves the v1 stage, authority, budget, capability, evidence, and conflict semantics and adds a **gated-convergence** control plane for checkpointed work.

The v1 contract remains supported. Use v2 only when progression between increments must be conditioned on explicit proof/review gates.

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

`executable-proof` and `adversarial-review` require independent isolation (`fresh-context`, `workspace`, `process`, or `host-native`). `human-approval` uses `human` isolation. A required gate that depends on an unavailable capability blocks progression; it never silently degrades to `not-run`.

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
