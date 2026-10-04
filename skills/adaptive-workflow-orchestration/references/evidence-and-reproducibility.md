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

## Live state, memory, and closure

For mutable targets, distinguish three identities:

1. **reference identity** — what the plan/oracle was derived from;
2. **candidate identity** — the exact state a gate evaluated;
3. **authoritative live identity** — the state that must still be true before mutation or closure.

Persisted ledgers and feedback are claims with provenance, not operational truth. Reconcile them against live state according to the declared freshness policy. A candidate change invalidates affected gate evidence. A live-state change may invalidate the premise itself.

Durable workflow memory must be explicit evidence: accepted/proven feedback, source/checkpoint identity, and the decision it affected. Never persist inferred preferences as if the user accepted them.

Where possible, encode mechanically enforceable guarantees in validators/scripts: identities, budgets, gate ordering, current-head checks, deduplication, packaging, and accounting.
