# Workflow Plan Contract

Contract: `workflow-plan/v1`

## At a Glance

Compatibility contract for existing material orchestration workflows. It defines authority, acyclic stages, resource-conflict rules, finite budgets, semantic capabilities/degradation, and evidence identities. It is a proposed/accepted control-flow artifact, not proof that workers executed. New runtime-adaptive work should use `dynamic-workflow-plan/v1`; new reference-grounded checkpoint promotion belongs to `checkpoint-convergence`.

## Contents

- Required top-level fields
- Authority
- Stages
- Dependency and conflict semantics
- Verification isolation
- Budgets
- Capabilities and degradation
- Evidence identities
- Strategy consistency

Use this contract for material task-specific orchestration. It is a proposed/accepted control-flow artifact, not proof that workers executed.

## Required top-level fields

- `contract`: exactly `workflow-plan/v1`.
- `workflow_id`: stable caller/run identity.
- `objective`: bounded task objective.
- `success_criteria`: one or more explicit criteria.
- `strategy`: one supported primary strategy.
- `authority`: owner, allowed/forbidden effects, and mutation scope.
- `stages`: non-empty acyclic stage list.
- `budgets`: finite global worker/parallel/retry/re-entry limits.
- `termination`: success predicate and terminal states.
- `capabilities`: required/optional semantic capabilities and degradation policy.
- `evidence`: material input/planner/evaluator identities.

## Authority

```json
{
  "owner": "mago",
  "allowed_effects": ["read-only"],
  "forbidden_effects": ["mutating", "external-side-effect"],
  "write_scope": []
}
```

`allowed_effects` and `forbidden_effects` use `read-only`, `mutating`, and `external-side-effect`. A stage may use only `read-only` or `mutating`.

If any mutating stage exists:

- `mutating` must be allowed and not forbidden;
- `write_scope` must be non-empty;
- every resource in every stage `write_set` must match at least one `write_scope` entry.

The validator uses conservative glob matching. Unknown or ambiguous scope should be narrowed or serialized rather than interpreted permissively.

## Stages

Each stage requires:

- `id` - unique non-empty id;
- `mode` - `single|parallel|pipeline|verify|synthesize|loop`;
- `work_source` - non-empty identity/ref explaining where work comes from;
- `depends_on` - stage ids that must complete first;
- `max_parallel` - positive integer within global ceilings;
- `isolation` - `shared-readonly|fresh-context|workspace|process|host-native|serial`;
- `effects` - `read-only|mutating`;
- `read_set` and `write_set` - resource ids/paths/globs;
- `success` - stage completion predicate;
- `on_failure` - `stop|continue-independent|retry|repair|escalate`.

`loop` additionally requires `max_iterations > 0`.

Read-only stages require an empty `write_set`. Mutating stages require a non-empty `write_set`.

## Dependency and conflict semantics

Dependencies must form a DAG outside the internal bounded behavior of a `loop` stage.

Two stages are potentially concurrent when neither transitively depends on the other and global `max_parallel > 1`.

For potentially concurrent stages, any overlapping resource where at least one stage writes is invalid:

- write/write overlap;
- write/read overlap;
- read/write overlap.

Add an ordering edge or change the resource/isolation design before execution. Do not rely on completion order chosen by the model/runtime.

## Verification isolation

A `verify` stage must use one of:

- `fresh-context`;
- `workspace`;
- `process`;
- `host-native`.

`serial` or `shared-readonly` alone does not establish independent verification.

## Budgets

Required:

- `max_workers > 0`;
- `max_parallel > 0` and `<= max_workers`;
- `max_retries_per_unit >= 0`;
- `max_reentries >= 0`.

Every stage `max_parallel` must be `<=` both global ceilings. A `retry` failure policy requires a non-zero retry budget.

## Capabilities and degradation

`required` and `optional` are unique **semantic capability ids** and must not overlap. They describe behavior the workflow needs; they are not external Agent Skill package names, vendor identifiers, installation paths, or model ids.

When `max_parallel > 1` and `parallelize-independent-work` is optional rather than required, `degradation.parallelize-independent-work` must be `serial` or `blocked`.

Do not infer host support from the plan. Host resolution is a separate late-binding step: the active worker may satisfy a semantic capability with a matching host-discovered Agent Skill, but that supporting skill remains subordinate to the active worker's authority and does not become lifecycle owner. Required unresolved capability blocks; optional unresolved capability follows only the declared semantics-preserving degradation.

## Evidence identities

Required non-empty identities:

- `input_identity` - source/task evidence used to plan;
- `planner_identity` - planner/controller/instruction identity;
- `evaluator_identity` - criteria/evaluator used to judge completion.

The plan does not embed its own identity. The validator emits canonical `plan_sha256`; execution traces bind to that hash.

## Strategy consistency

The validator enforces hard consistency where unambiguous:

- `single` requires one stage and global worker/parallel ceilings of 1;
- `bounded-loop` requires at least one `loop` stage;
- `adversarial-verify` requires at least one `verify` stage.

Other strategy-shape observations may be warnings because valid composed workflows can vary.
