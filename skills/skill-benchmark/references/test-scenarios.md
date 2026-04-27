# Test Scenario Methodology

Use this guide to create measurable behavioral benchmarks for a target skill.

## Scenario categories

Each benchmark should include at least 20 scenarios:

1. `should_activate`: 5 prompts where the skill should clearly activate.
2. `should_not_activate`: 5 prompts where the skill should not activate.
3. `ambiguous`: 5 prompts where the skill must clarify, choose a safe default, or proceed with explicit assumptions.
4. `edge_case`: 5 prompts involving missing files, incomplete inputs, conflicting instructions, large content, invalid paths, or unsupported output requests.

## Scenario table schema

Use this table when results are manually recorded:

| ID | Category | Prompt | Expected activation | Actual activation | Output conforms | Quality score 0-5 | Needs rework | Notes |
|---|---|---|---|---|---|---:|---|---|

## Optional JSON result schema

The generator script can consume this shape:

```json
[
  {
    "id": "A1",
    "category": "should_activate",
    "prompt": "Benchmark the skill at skills/prd-banking-flows",
    "expected_activation": true,
    "actual_activation": true,
    "output_conforms": true,
    "quality_score": 5,
    "needs_rework": false,
    "notes": "Generated the expected report."
  }
]
```

Allowed categories:

- `should_activate`
- `should_not_activate`
- `ambiguous`
- `edge_case`

## Deterministic result validation

When scenario results are supplied as JSON, run the bundled validator before computing measured metrics:

```bash
python3 -S scripts/validate_scenario_results.py --results <scenario-results-json> --json-output <validation-output-json>
```

The validator requires an array of result objects with stable IDs, allowed categories, boolean expected and actual activation fields, boolean or null conformance and rework fields, and a quality score from 0 to 5 when provided. If validation fails, do not calculate measured precision, recall, robustness, output conformance, or rework rate from that file.

## Metric formulas

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / all executed scenarios.
- Robustness = passed edge cases / all executed edge cases.
- Rework rate = scenarios needing rework / all executed scenarios.
- Average quality score = sum of quality scores / scored scenarios.

## Status labels

Use these labels:

- `measured`: evidence was executed or supplied.
- `planned`: scenario exists but was not executed.
- `blocked`: scenario could not be executed due missing environment, tool, file, or permission.
- `not applicable`: scenario does not apply to the target skill.

## Interpretation

A target skill is behaviorally mature when:

- Activation precision is at least 90 percent.
- Activation recall is at least 85 percent.
- Output conformance is at least 90 percent.
- Robustness is at least 75 percent.
- Rework rate is at most 10 percent.

Never report these as measured unless execution evidence exists.
