# Scenario Suite

Use this reference when creating behavioral tests for a hardened skill.

## Minimum scenario set

Create at least 20 scenarios when behavior is in scope:

- 5 `should_activate` prompts;
- 5 `should_not_activate` prompts;
- 5 `ambiguous` prompts;
- 5 `edge_case` prompts.

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

## Scoring rules

Only mark a metric as measured when the scenario was actually executed or the user supplied execution results.

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / all executed scenarios.
- Robustness = passed edge cases / all executed edge cases.
- Rework rate = scenarios needing rework / all executed scenarios.

## Quality bar

A hardened skill should target:

- activation precision at least 90 percent;
- activation recall at least 85 percent;
- output conformance at least 90 percent;
- robustness at least 75 percent;
- rework rate at most 10 percent.

## Scenario file placement

For package-level hardening, keep reusable planned scenarios under `examples/` unless the target skill already owns a stricter scenario path. A scenario example file should be referenced from `SKILL.md`, should contain all four categories, and should keep execution fields null until results are actually measured.

The bundled `examples/hardening-scenarios.json` demonstrates the minimum category mix for this skill. Use it as a calibration example, not as evidence that another target skill's scenarios passed.
