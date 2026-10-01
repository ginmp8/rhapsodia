# Evidence and Reproducibility

## Identity chain

Keep these separate when material:

1. `input_identity` - exact task/source evidence used for planning;
2. `planner_identity` - controller/instructions/model/configuration that produced or selected the plan;
3. `plan_sha256` - canonical accepted workflow-plan bytes/structure;
4. `execution_trace_identity` - one actual run of that plan;
5. `evaluator_identity` - completion/quality criteria;
6. final result/artifact identity.

Do not collapse them into one generic run id.

## Planning vs execution variance

**Planning variance** changes decomposition, strategy, worker count, dependencies, verification topology, or budgets.

**Execution variance** occurs when the same accepted plan produces different worker results/order/tool observations.

To evaluate planner quality, freeze input/evaluator and compare plans. To evaluate execution repeatability, freeze one accepted plan and compare traces. If both change, do not attribute the delta to one layer without additional evidence.

## Evaluator freeze

Freeze deciding evaluators before candidate/plan mutation when making an improvement claim. Changing eval prompts, fixtures, expected outputs, thresholds, or evaluator logic during the same comparison invalidates comparability unless explicitly re-baselined.

## Independent verification

Record whether the verifier had:

- fresh/isolated context;
- producer result only versus producer hidden history;
- evaluator-only information;
- separate tool/source access.

"Independent" is an evidence property, not a role label.

## Evidence labels

Use `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked` consistently. A valid plan is structural evidence, not runtime evidence.
