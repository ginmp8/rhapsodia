# Workflow Execution Evidence

## Purpose

Capture evidence about the orchestration layer separately from the target skill's behavior. This is useful when one scenario run itself uses adaptive multi-agent or multi-stage execution.

## Identity separation

Keep these identities distinct when available:

- target skill identity;
- evaluator/scenario identity;
- planner/controller identity;
- accepted workflow-plan identity;
- execution-trace identity;
- final artifact/result identity.

A change in plan identity means the orchestration policy changed even if the target skill did not. A change in trace identity under the same plan is execution variability.

## Optional workflow envelope

A workflow-aware execution record may include:

```text
workflow_execution:
  planner_identity_sha256
  workflow_plan_identity_sha256
  strategy
  stage_count
  worker_count
  max_parallelism
  fresh_context_verification
  retries
  reentries
  terminal_reason
  execution_trace_sha256
```

Use `assets/templates/workflow-execution-evidence.json.template` when a standalone sidecar is useful.

## Evidence rules

- The workflow plan must be accepted/frozen before a run used for measured comparison.
- Compared runs must use the same material plan/evaluator/source identities unless the question is specifically plan comparison.
- Independent-verifier claims require evidence that the verifier did not receive evaluator-only answers or the producer's hidden reasoning/history.
- Planned worker/stage topology is not executed evidence.
- A trace proves only what it actually captures; unavailable trace detail remains unavailable.
- A structurally valid workflow does not prove target-skill quality.

## Comparisons

### Compare plans

Hold objective, material inputs, authority, evaluator, and host capability profile stable; vary the plan. Evaluate coverage, correctness, cost/latency when measured, and regressions.

### Compare executions

Hold the accepted plan stable; rerun workers. This measures execution variance rather than planning variance.

Do not mix both changes and attribute the result to only one layer.
