# Scenario Suite

Use when creating planned behavioral tests for a hardened skill. The package contract follows the current host-neutral Harness scenario shape; execution evidence stays outside the scenario definition.

## Minimum set

Create at least 20 scenarios: 5 `should_activate`, 5 `should_not_activate`, 5 `ambiguous`, and 5 `edge_case`. Add `regression` or `adversarial` cases when material.

## JSON contract

Each scenario requires `id`, `type`, `prompt`, `expected_behavior`, and a non-empty string list `acceptance_criteria`. Allowed `type` values are `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`, `regression`, and `adversarial`.

```json
{
  "target_skill": "skill-hardening",
  "status": "planned",
  "schema_version": "2.0",
  "scenarios": [
    {
      "id": "A001",
      "type": "should_activate",
      "prompt": "Harden the uploaded invoice-parser skill and package it.",
      "expected_behavior": "Runs audit, applies package-level improvements, validates, and packages only after gates pass.",
      "acceptance_criteria": [
        "skill-hardening is selected for an existing skill package",
        "package success is claimed only after applicable gates pass"
      ]
    }
  ]
}
```

Do not keep legacy `category`/`expected_activation` fields solely for backward compatibility once all active consumers use the current `type` contract. If an active consumer requires another schema, treat that as an explicit peer-contract migration rather than silently maintaining two sources of truth.

## Evidence and scoring

Scenario files are planned definitions until executed. Record actual activation/output results in external run evidence tied to the exact suite/evaluator identity; do not mutate the planned suite after baseline freeze to make a candidate pass.

Metrics are measured only from executed or supplied results: activation precision, activation recall, output conformance, edge-case robustness, and rework rate. Static schema validation never proves these behavioral metrics.

## Placement

Use `evals/activation-scenarios.json` as the package's planned activation/boundary suite. `examples/hardening-scenarios.json` is calibration only. `assets/templates/scenario-suite.json.template` is the reusable starting shape.
