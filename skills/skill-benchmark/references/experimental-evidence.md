# Experimental Behavioral Evidence

Use this reference for measured behavioral comparison. Static score changes are not behavioral capability deltas.

## Evidence versions

- **v2** remains readable for backward compatibility. It represents one observation per scenario and supports directional deltas only.
- **v3** is the preferred contract for new stochastic/model-agent evaluations. It binds repeated trials to evaluator, scenario-suite, and runtime-profile identities.

A v3 envelope requires `schema_version: 3`, `evidence_origin`, `arm_type`, evaluator/scenario/runtime SHA-256 identities, `suite_role`, `distribution_profile`, and scenarios containing `trials`.

Supported arms are `baseline`, `parent`, `candidate`, `without-skill`, `length-control`, and `single`. `length-control` is optional and estimates distraction/context-length effects using an irrelevant skill/context of materially comparable size; it never replaces the prior-version baseline.

## Strong claim policy

Use paired scenario/trial keys across compared arms. For v3 the arm comparator reports:

- point estimate and raw delta;
- deterministic 95% paired bootstrap interval;
- a predeclared practical-effect threshold;
- `claim_classification`: `improved`, `regressed`, `practically-unchanged`, `inconclusive`, `unmeasured`, or `not-comparable`.

The legacy `classification` field remains directional for compatibility. Do not use it alone for a strong stochastic improvement claim. v2 evidence is intentionally `inconclusive` for strong stochastic claims because it has no repeated-trial uncertainty contract.

## Runtime identity

Behavioral claims are scoped to the tested `runtime_profile_sha256` and material host/model/harness/tool configuration. Structural multi-host portability does not imply behavioral portability. Changed runtime identity makes a strict v3 delta non-comparable unless the experiment explicitly controls that difference.

## Efficiency

When trials expose them, report mean `input_tokens`, `output_tokens`, `total_tokens`, `latency_ms`, `tool_calls`, and `cost_usd`. Keep efficiency separate from capability metrics. Never synthesize one overall score unless a weighting policy and directions were frozen before execution.

## Grader calibration

For `grader_type: llm` or `mixed`, record calibration status and, when available, calibration-set identity, human agreement, position balancing, length control, and abstention support. Hidden-evaluator leakage controls still apply. Calibration failure blocks strong quality claims; missing calibration is visible evidence debt, not a pass.

## Suite semantics

`suite_role` is one of `diagnostic`, `capability`, `regression`, or `holdout`. `distribution_profile` is `diagnostic-balanced`, `production-representative`, or `custom`. Balanced diagnostic precision/recall must not be described as production prevalence without representative sampling evidence.
