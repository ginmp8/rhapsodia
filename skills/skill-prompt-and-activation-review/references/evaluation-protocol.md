# Activation Evaluation Protocol

Protocol version: `1.0.0`

Use this protocol when activation/boundary text changes or when a user asks for evidence beyond static review. It is deliberately host-neutral: a host adapter or external harness may execute routing, but the evidence contract remains the same.

## Evidence layers

Keep these distinct:

- `static-contract`: deterministic validation of suite shape, traceability, evidence identity, and package rules;
- `static-adjudication`: linguistic review performed without observing host auto-invocation;
- `host-routing`: actual observed invocation/routing for a scenario in an isolated host/harness;
- `runtime`: downstream tool/application behavior after routing.

Only `host-routing` may support activation precision/recall or routing-regression claims.

## Canonical suite

`evals/activation-scenarios.json` is the package's canonical seed suite. For a target-specific review, add only scenarios needed for the changed surface and preserve the original scenario IDs/expectations used in the comparison.

Before baseline execution:

1. validate the suite with `scripts/validate_activation_suite.py`;
2. freeze the exact suite plus evaluator/rubric assets with `scripts/freeze_activation_evaluator.py`;
3. classify evaluator assets as candidate-visible or evaluator-only using `references/evaluator-visibility.md`;
4. record the resulting `evaluator_sha256` and the canonical suite SHA-256;
5. do not edit frozen assets after seeing candidate results.

If `evaluator_visibility=hidden`, the candidate execution must not receive evaluator-only rubrics, expected routes, private holdout labels, grader prompts, or post-run adjudication. Exposure invalidates blind-evaluation claims and the comparison must be rerun with a clean boundary or reclassified as candidate-visible/open-rubric evidence.

If the evaluator is wrong, invalidate the comparison, fix it separately, freeze a new evaluator, and restart both arms.

## Baseline/candidate pairing

For any before/after claim:

- run baseline and candidate with exactly the same scenario IDs, prompts, files, expectations, evaluator identity, and host configuration that materially affects routing;
- record baseline and candidate package/source identity separately;
- preserve holdout cases from candidate authoring when using them for robustness evidence;
- do not drop difficult or failing scenarios after the baseline run;
- compare using `scripts/compare_activation_evidence.py`.

A static review may recommend a candidate without host execution, but the report must say that behavioral evidence was not obtained.


## Self-generated activation candidate

When the activation/prompt candidate was produced by a self-improving version of the same skill family, keep generation provenance separate from routing evaluation.

Record when available:

```text
candidate_origin = self-generated
generation_id
controller_identity
baseline_identity
candidate_identity
```

Rules:

- the controller that authored the candidate must not see evaluator-only holdout routes, private labels, grader prompts, or post-run adjudication when blind evaluation is claimed;
- the candidate execution must remain equally blind to evaluator-only assets;
- baseline and candidate must use materially equivalent host/routing configuration in addition to the same frozen suite/evaluator;
- changing host configuration, evaluator visibility, expected routes, or holdout membership between arms makes behavioral routing deltas non-comparable;
- controller identity is provenance, not an activation result;
- this reviewer evaluates activation/prompt behavior only. It does not select or sequence unrelated improvement specialists and it does not own candidate promotion.

A self-generated candidate may still receive a static rewrite recommendation when host execution is unavailable, but any behavioral activation claim remains blocked until the normal host-routing evidence gate is satisfied.

## Result evidence contract

A comparison arm should provide JSON like:

```json
{
  "evidence_version": 1,
  "suite_sha256": "...",
  "evaluator_sha256": "...",
  "execution_kind": "host-routing",
  "evidence_status": "executed",
  "host_profile": "documented capability/profile identity",
  "evaluator_visibility": "hidden",
  "candidate_saw_evaluator_only_assets": false,
  "trace_manifest_sha256": "optional 64-hex trace identity",
  "cases": [
    {
      "id": "act-001",
      "observed_route": "activate",
      "activated": true,
      "evidence": "runner-specific trace/reference"
    }
  ]
}
```

Allowed `evidence_status`: `executed`, `supplied`, `planned`, `blocked`. `evaluator_visibility` may be `hidden`, `candidate-visible`, or `not-applicable`. A hidden evaluator requires `candidate_saw_evaluator_only_assets=false`. `trace_manifest_sha256` is optional because not every host exposes a usable trace.

Use `supplied` when a user gives results that were not independently executed in the current workflow. `planned` and `blocked` never support measured improvement claims.

## False-positive/false-negative metrics

Binary precision/recall applies only to scenarios whose frozen expectation is `activate`, `activate-constrained`, or `do-not-activate` and whose runner records a boolean `activated` value.

Exclude `ambiguous`, `split-handoff`, and rejection-policy scenarios from binary precision/recall unless the frozen evaluator explicitly defines a binary expectation before both arms run.

A scenario may still be a routing regression even when it is excluded from precision/recall if its full `observed_route` no longer matches the frozen expected route.

## Claim rules

Use this vocabulary:

- `proposed`: suggested but not validated;
- `observed-static`: directly supported by text/package inspection or deterministic static validator;
- `supplied`: based on user-provided execution evidence;
- `executed`: actually run in the current workflow;
- `derived`: deterministic calculation from executed/supplied evidence;
- `blocked`: required evidence could not be obtained.

Never report activation precision, activation recall, behavioral improvement, or regression reduction from `static-contract` or `static-adjudication` evidence alone.

## Gate order

1. target identity and scope fixed;
2. suite validates;
3. evaluator frozen;
4. baseline evidence captured;
5. candidate authored without changing evaluator;
6. candidate evidence captured with same cases;
7. evaluator manifest verifies unchanged;
8. comparison passes identity, host-profile, and evaluator-visibility/leakage gates;
9. target package validators/tests pass;
10. final candidate freezes; any later edit restarts affected validation.

## Stop conditions

Stop the comparison when:

- suite/evaluator identity differs between arms;
- materially relevant host profiles differ between arms;
- hidden evaluator assets were exposed to either evaluated arm or leakage status is unresolved;
- scenario IDs differ;
- a frozen expectation was edited after seeing an outcome;
- required routing evidence is unavailable for a requested behavioral metric;
- the only way to pass is to weaken a boundary, evidence rule, or evaluator;
- host-specific invocation behavior is undocumented enough that the observed route cannot be interpreted reliably.
