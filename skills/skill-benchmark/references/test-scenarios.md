# Behavioral Scenario Evidence

Use this contract for activation/output metrics.

## Recommended suite

Include at least 20 scenarios:

1. `should_activate`: 5 clear activations.
2. `should_not_activate`: 5 clear non-activations.
3. `ambiguous`: 5 prompts requiring clarification/explicit assumptions.
4. `edge_case`: 5 missing/invalid/conflicting/unsupported cases.

## Portable v2 result envelope

Prefer identity-bound evidence:

```json
{
  "schema_version": 2,
  "evidence_origin": "executed",
  "arm_type": "candidate",
  "target_identity_sha256": "<64 hex>",
  "evaluator_identity_sha256": "<64 hex>",
  "scenario_suite_sha256": "<64 hex or suite identity>",
  "host_profile": "<material host/runtime profile>",
  "trace_manifest_sha256": "<64 hex when available>",
  "evaluator_visibility": "hidden",
  "candidate_saw_evaluator_only_assets": false,
  "scenarios": [
    {
      "id": "A1",
      "category": "should_activate",
      "prompt": "Benchmark this skill package.",
      "expected_activation": true,
      "actual_activation": true,
      "output_conforms": true,
      "quality_score": 5,
      "needs_rework": false,
      "notes": "Expected report produced."
    }
  ]
}
```

Legacy top-level arrays remain accepted for backwards compatibility, but validation marks them `unpinned`. Do not use unpinned evidence for strict before/after improvement claims.

`arm_type` may be `without-skill`, `baseline`, `candidate`, or `single`. For `without-skill`, omit `target_identity_sha256`. `evaluator_visibility` may be `hidden`, `candidate-visible`, or `not-applicable`. A `hidden` evaluator requires `candidate_saw_evaluator_only_assets=false`; otherwise blind-evaluation claims are invalid. Trace identity is optional because not every host exposes execution traces.

Allowed categories: `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`.

## Validation

```text
<PYTHON> scripts/validate_scenario_results.py \
  --results <RESULTS_JSON> \
  --json-output <VALIDATION_JSON>
```

Rows require stable `id`, category, prompt, expected/actual activation, output conformance, quality score 0-5 or null, and rework boolean/null.

## Metrics

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / executed rows with conformance evidence.
- Robustness = passing edge cases / executed edge cases.
- Rework rate = rows requiring rework / executed rows.
- Criteria coverage remains `not measured` unless criteria-level evidence exists.

## Status labels

- `measured`: executed, identity-bound evidence.
- `supplied`: valid supplied evidence; state whether pinned/unpinned.
- `planned`: scenario exists but was not executed.
- `blocked`: required capability/evidence unavailable.
- `not applicable`: metric/scenario does not apply.

Never convert planned or malformed evidence into measured metrics.
