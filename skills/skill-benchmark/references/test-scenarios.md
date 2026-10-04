# Behavioral Scenario Evidence

Use this contract for activation/output metrics. Read `experimental-evidence.md` for repeated-trial comparison, uncertainty, runtime identity, efficiency, and strong-claim rules.

## Recommended diagnostic suite

For a compact balanced diagnostic suite, include at least 20 scenarios: 5 `should_activate`, 5 `should_not_activate`, 5 `ambiguous`, and 5 `edge_case`. This balance is for diagnostic coverage; it does not estimate production prevalence unless representative sampling evidence exists.

## Evidence versions

### v2 compatibility envelope

Schema v2 remains valid for existing evidence. It contains one result row per scenario and supports activation precision/recall, output conformance, robustness, and rework rate. Because it lacks repeated trials/runtime identity, v2 comparisons are directional evidence only for stochastic agents and must not support a strong reliability/improvement claim.

### v3 preferred envelope

New measured model/agent runs should use `schema_version: 3`. It adds repeated `trials`, `runtime_profile_sha256`, `suite_role`, `distribution_profile`, optional efficiency observations, and optional model-grader calibration metadata. Use `assets/templates/scenario-results-v3.json.template`.

Validate either version with:

```text
<PYTHON> scripts/validate_scenario_results.py --results <RESULTS_JSON> --json-output <VALIDATION_JSON>
```

Allowed categories: `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`. Allowed v3 suite roles: `diagnostic`, `capability`, `regression`, `holdout`.

## Metrics

- Activation precision = correct actual activations / all actual activations.
- Activation recall = correct actual activations / all expected activations.
- Output conformance = conforming outputs / executed rows with conformance evidence.
- Robustness = passing edge cases / executed edge cases.
- Rework rate = rows requiring rework / executed rows.
- Efficiency metrics, when supplied, remain separate: input/output/total tokens, latency, tool calls, cost.
- Skill behavior constraint coverage remains `not measured` unless valid coverage evidence exists; use `skill-coverage.md`.

## Status labels

- `measured`: executed, identity-bound evidence.
- `supplied`: valid supplied evidence; state pinned/unpinned.
- `planned`: scenario exists but was not executed.
- `blocked`: required capability/evidence unavailable.
- `not applicable`: metric/scenario does not apply.

Never convert planned, malformed, uncalibrated, contaminated, or non-comparable evidence into a measured strong claim.
