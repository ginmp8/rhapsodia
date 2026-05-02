# Test Scenario Methodology

Use this guide for measurable behavioral benchmarks.

## Scenario set

Include at least 20 scenarios:

1. `should_activate`: 5 clear activation prompts.
2. `should_not_activate`: 5 clear non-activation prompts.
3. `ambiguous`: 5 prompts requiring clarification, safe default, or explicit assumptions.
4. `edge_case`: 5 prompts with missing files, incomplete inputs, conflicts, large content, invalid paths, or unsupported outputs.

## Manual result table

| ID | Category | Prompt | Expected activation | Actual activation | Output conforms | Quality score 0-5 | Needs rework | Notes |
|---|---|---|---|---|---|---:|---|---|

## Optional JSON result schema

Generator-compatible shape:

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

Allowed categories: `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`.

## Deterministic validation

Validate supplied JSON before computing measured metrics:

```bash
python3 -S scripts/validate_scenario_results.py --results <scenario-results-json> --json-output <validation-output-json>
```

The validator requires an array of stable result objects; allowed category; boolean expected/actual activation; boolean or null conformance/rework; quality score 0-5 when present. If validation fails, do not calculate measured precision, recall, robustness, output conformance, or rework rate from that file.

## Formulas

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / all executed scenarios.
- Robustness = passed edge cases / all executed edge cases.
- Rework rate = scenarios needing rework / all executed scenarios.
- Average quality score = sum of quality scores / scored scenarios.

## Status labels

- `measured`: executed or supplied evidence exists.
- `planned`: scenario exists but was not executed.
- `blocked`: missing environment, tool, file, or permission.
- `not applicable`: scenario does not apply.

## Interpretation

Behaviorally mature target: activation precision >= 90 percent; activation recall >= 85 percent; output conformance >= 90 percent; robustness >= 75 percent; rework rate <= 10 percent. Never report these as measured without execution evidence.
