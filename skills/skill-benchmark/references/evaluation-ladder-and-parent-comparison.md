# Evaluation Ladder and Parent Comparison

Use when the caller wants staged evaluation, many candidate experiments, or parent-child attribution without paying for a full benchmark on every candidate.

## Evaluation levels

- `L0-structural`: identity, package structure, local refs, protected paths, syntax/schema.
- `L1-deterministic`: target-owned validators/tests/static contracts.
- `L2-focused`: metrics/scenarios tied directly to the selected hypothesis and affected capabilities.
- `L3-harness`: broader regression/adversarial scenario execution and isolation/leakage evidence.
- `L4-benchmark`: full comparable benchmark arms.
- `L5-holdout`: independent/evaluator-only holdout for promotion claims vulnerable to evaluator overfitting.

Skill Benchmark normally owns `L4`; it may consume lower/higher-level evidence but must label what it did not execute. Do not require a full benchmark when the caller only needs a lower-level gate and makes no stronger claim.

## Parent comparison

For iterative optimization, allow a `parent` reference in addition to baseline/candidate. Parent is the direct ancestor used to attribute the current transformation; baseline is the stable regression reference. They may be the same but serve different semantic roles.

Report:

- candidate vs parent: local transformation effect;
- candidate vs baseline: cumulative regression/improvement;
- candidate vs without-skill: incremental skill value when relevant.

All strict deltas require comparable evaluator/scenario/runtime identity.

## Hard gates before metrics

Never choose a candidate because a composite score compensates for a blocking regression. First apply required identity/activation/semantic/safety/validation/delivery gates; then compare eligible metrics. When several candidates are non-dominated across different metrics, report the frontier/metrics rather than inventing a winner unless the caller supplied a frozen weighting policy.

## Historical results

Prior benchmark results may be consumed as provenance-bound evidence. Do not merge metrics from different evaluator/scenario identities into a synthetic delta. Do not convert one target's winning strategy into global benchmark policy.
