# Control Arms and Capability Delta

## At a Glance

- **Purpose:** Define causal roles and comparability rules for `baseline`, `candidate`, `parent`, `without-skill`, and optional `length-control` benchmark arms, plus capability-delta claim semantics.
- **Load when:** Comparing skill versions/candidates, measuring incremental skill value, evaluating self-improvement provenance, using hidden evaluators, or interpreting capability/efficiency deltas.
- **Decision impact:** Determines which arm answers regression versus incremental-value questions, when a delta is comparable, how evaluator visibility/provenance constrain claims, and when uncertainty requires `inconclusive` rather than improvement/regression language.
- **Do not load when:** Running a standalone single-skill maturity benchmark with no cross-arm or capability-delta claim.

## Contents

- Arm roles
- Comparability contract
- Self-improvement provenance
- Evaluator visibility
- Trace provenance
- Capability delta
- Claims
- Length-matched context control
- Uncertainty-aware strong claims

## Arm roles

- `without-skill`: the same task/scenarios run without the target skill. Use to estimate incremental skill value.
- `baseline`: the immutable prior skill version. This is the primary regression baseline for existing-skill updates.
- `candidate`: the proposed skill version.
- `parent`: optional direct ancestor of a candidate in an iterative experiment. Use for local transformation attribution; it does not replace the stable regression `baseline`.
  Parent scenario evidence uses `arm_type: parent`; strict comparison still requires the same evaluator/scenario/runtime identities.
- `single`: a standalone run not intended for a strict delta.

For a net-new skill, `without-skill` may be the only meaningful baseline. For an existing-skill update, do not replace the prior-version `baseline` with `without-skill`; they answer different questions.

## Comparability contract

A behavioral delta is comparable only when the arms use the same:

- evaluator identity;
- scenario-suite identity;
- scenario IDs and expected outcomes;
- materially relevant host/runtime configuration;
- evidence schema and metric definitions.

Target identity is expected to differ between baseline and candidate. The `without-skill` arm intentionally has no target identity.

If host/runtime profiles differ materially, report standalone arm metrics and mark the delta `not-comparable` unless the benchmark contract explicitly controls for that difference.


## Self-improvement provenance

When a skill generates a candidate for itself, keep **generation provenance** separate from benchmark arms.

- `controller`: the immutable version that produced the candidate. It is provenance, not automatically a comparison arm.
- `baseline`: the immutable prior target used for regression comparison.
- `candidate`: the frozen proposed target.
- `without-skill`: optional host/model control for incremental-value questions.

A self-improvement result envelope may include:

```text
self_improvement.generation_id
self_improvement.controller_identity_sha256
self_improvement.baseline_identity_sha256
self_improvement.candidate_identity_sha256
```

For a strict baseline/candidate comparison:

- both arms must name the same generation and controller identity;
- the baseline arm target identity must match `baseline_identity_sha256`;
- the candidate arm target identity must match `candidate_identity_sha256`;
- controller and candidate identities must differ for a material self-improvement candidate;
- the controller identity must not replace the baseline arm;
- `without-skill` remains optional and answers incremental value, not generational regression.

If generation/controller provenance differs, classify the delta `not-comparable` even when evaluator and scenario hashes match.

## Evaluator visibility

When using hidden graders, private expected answers, or holdouts, record `evaluator_visibility=hidden` and prove `candidate_saw_evaluator_only_assets=false`. If the evaluated candidate can read the evaluator-only material, the result may still be usable as an open-rubric run, but it is not blind/hidden evaluation.

Do not hide rubrics that are legitimately part of the task. Mark them `candidate-visible` instead.

## Trace provenance

When the runner exposes an execution trace, hash or otherwise identify the trace manifest and bind it to the result envelope. Do not embed secrets, credentials, or unnecessary sensitive payloads in benchmark results.

A missing trace does not automatically invalidate behavioral evidence unless trace inspection is part of the declared acceptance contract. Record it as unavailable rather than fabricating one.

## Capability delta

Compute delta only from numeric metrics that are valid in both compared arms.

For each metric classify:

- `improved`: candidate > reference for higher-is-better metrics, or candidate < reference for lower-is-better metrics;
- `regressed`: inverse of the above;
- `unchanged`: equal within the exact deterministic metric representation;
- `unmeasured`: one or both arms lack eligible evidence;
- `not-comparable`: identity/configuration gates failed.

Default direction:

- higher is better: activation precision, activation recall, output conformance, robustness;
- lower is better: rework rate.

Do not collapse capability delta into one composite score unless a frozen rubric predeclares weights and direction before the runs.

## Claims

- Candidate vs baseline supports regression/improvement claims for an existing skill.
- Candidate vs without-skill supports incremental-value claims.
- Baseline vs without-skill can show whether the prior skill already added value.
- A static score delta is not a behavioral capability delta.
- Planned scenarios, unpinned evidence, changed evaluators, or leaked hidden graders do not support strict capability-delta claims.

## Length-matched context control

An optional `length-control` arm uses irrelevant context/skill content of materially comparable size to the candidate. It estimates context-length/distraction effects and is diagnostic only. It never replaces `baseline`, `parent`, or `without-skill` because those answer different causal questions.

## Uncertainty-aware strong claims

For v3 stochastic evidence, use repeated paired trials and the comparator's uncertainty output. Keep the legacy directional `classification` for compatibility, but base strong improvement/regression language on `claim_classification`. `inconclusive` is a valid and preferred outcome when the interval crosses the practical-effect threshold. Do not equate statistical separation with practical importance.

Efficiency deltas are reported separately from capability deltas. Do not compensate a capability regression with lower token/cost usage through an undeclared composite score.
