# Scenario Suite

## Principle

There is no universal scenario-count gate. Scenario sufficiency depends on the claim, activation surface, risk, neighboring skills, and evaluator quality. Predeclare required categories and minimum coverage before mutation; definitions remain planned evidence until executed.

## Categories

Core routing categories:

- `should_activate`
- `should_not_activate`
- `ambiguous`
- `edge_case`

Add when material:

- `coexistence`: the target and another legitimate skill both exist; verify correct division/routing.
- `semantic_collision`: a neighboring description shares terminology; verify the target does not steal unrelated requests.
- `regression`: known past failure.
- `adversarial`: attempts to bypass authority, scope, safety, or evaluator assumptions.

## JSON contract

Each scenario requires `id`, `type`, `prompt`, `expected_behavior`, and a non-empty string list `acceptance_criteria`. `schema_version`, target identity, and suite status may live at the top level.

The bundled structural validator defaults to at least one example of each core category only when scenarios are explicitly required. That default validates coverage shape, not statistical or behavioral sufficiency. Use a larger frozen suite, holdout cases, and repeated trials when the claim requires them.

## Metrics and execution

Only executed/supplied results can support activation precision/recall, output conformance, coexistence accuracy, collision rate, edge robustness, or rework metrics. Keep planned suite definitions separate from run evidence and freeze deciding scenarios before candidate mutation.

Use identical prompts/files/evaluator versions for baseline and candidate comparisons. Strong stochastic reliability claims require repeated trials and environment comparability; one successful stochastic run is not reliability proof.
