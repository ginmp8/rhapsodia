# Scenario Guidelines

Use when creating or repairing scenario suites.

## Minimum categories

Maintain at least 5 prompts each for `should_activate`, `should_not_activate`, `ambiguous`, and `edge_case`; optionally add `regression` from known failures and `adversarial` for boundary pressure.

## Scenario schema

```json
{
  "id": "A001",
  "category": "should_activate",
  "prompt": "Audit this target skill for inconsistent ownership and package it if repaired.",
  "expected_activation": true,
  "expected_behavior": "Runs baseline audit, repairs only allowed target files, validates, and packages only after gates pass.",
  "actual_activation": null,
  "output_conforms": null,
  "quality_score": null,
  "needs_rework": null,
  "notes": "planned"
}
```

## Measurement policy

Keep `actual_activation`, `output_conforms`, `quality_score`, and `needs_rework` as `null` until prompts are executed or the user supplies validated results. Planned scenarios show coverage design, not measured performance.

## Boundary prompts

Include: multiple `SKILL.md` roots; mixed governance/architecture ownership; unreferenced useful templates; undocumented scripts; benchmark request without repair; application-code implementation request; request to edit evaluator fixtures to pass.
