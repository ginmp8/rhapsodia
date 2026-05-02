# Scenario Suite

Use when creating behavioral tests for a hardened skill.

## Minimum set

Create at least 20 scenarios: 5 `should_activate`, 5 `should_not_activate`, 5 `ambiguous`, 5 `edge_case`.

## JSON schema

```json
[
  {
    "id": "A001",
    "category": "should_activate",
    "prompt": "Harden the uploaded invoice-parser skill and package it.",
    "expected_activation": true,
    "expected_behavior": "Runs audit, applies package-level improvements, validates, and packages only after gates pass.",
    "actual_activation": null,
    "output_conforms": null,
    "quality_score": null,
    "needs_rework": null,
    "notes": "planned"
  }
]
```

## Scoring

Metrics are measured only after scenario execution or user-supplied execution results.

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / executed scenarios.
- Robustness = passed edge cases / executed edge cases.
- Rework rate = scenarios needing rework / executed scenarios.

## Quality bar

Targets: activation precision >= 90%; recall >= 85%; output conformance >= 90%; robustness >= 75%; rework rate <= 10%.

## Placement

For package-level hardening, keep reusable planned scenarios under `examples/` unless the target owns a stricter path. Scenario examples must be referenced from `SKILL.md`, cover all four core categories, and keep execution fields null until measured; repeated null execution fields may be stored once as shared defaults.

`examples/hardening-scenarios.json` is calibration, not evidence that another target skill's scenarios passed.
