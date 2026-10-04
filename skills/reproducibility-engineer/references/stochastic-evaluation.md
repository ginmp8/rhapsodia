# Stochastic Evaluation Profile

## Purpose

Use this profile when the claim depends on repeated stochastic execution: agent behavior, model judgments, subjective graders, retries with model choice, or any workflow where one successful trial is not enough evidence of reliability.

A single run may prove a failure. It rarely proves repeatable improvement.

## Contract

Use `assets/schemas/stochastic-evaluation.schema.json` and validate with:

```text
<PYTHON> scripts/validate_execution_evidence.py --kind stochastic --input <STOCHASTIC-EVAL.json>
```

The validator derives counts, empirical success rate, a Wilson 95% interval, and `pass_power[k]` values from the recorded trials.

## Trial semantics

- Keep scenario/input/evaluator identities fixed across paired baseline/candidate arms unless the experiment explicitly tests one of them.
- Use fresh/isolated state between trials when independence is part of the claim.
- Record `success`, `failure`, or `unknown`; unknown counts conservatively as non-success in reliability metrics.
- Predeclare the stop rule and maximum trial budget. For `fixed-trials`, a completed result must contain exactly that many trials.
- Record ties explicitly in paired reviewer analysis rather than forcing a win; use `paired_sign_test.py` when win/loss testing is the appropriate metric.

## Reliability under repetition

`pass_power[k]` is computed as `p^k`, where `p` is the observed success fraction. It is a simple independence-model estimate of succeeding in all `k` equivalent trials, not a direct observation and not proof that trials are independent.

Use it alongside, not instead of:

- raw trial outcomes;
- interval/uncertainty;
- failure mode counts;
- paired baseline/candidate evidence;
- holdout or independent replication when the claim is strong.

Do not optimize only a saturated average success metric; add a non-saturated reliability or failure metric.

## LLM-as-judge

When `evaluator.kind = llm-judge`:

- record stable judge identity/configuration when available;
- record calibration status and calibration evidence identity when available;
- do not treat temperature zero as deterministic identity;
- keep the judge/evaluator frozen independently from the candidate;
- strong claims require calibration stronger than `unknown`.

## Promotion strength

Use claim levels proportionally:

- `exploratory` - useful directional evidence; no broad reliability claim;
- `standard` - repeated evidence under the declared evaluator/environment;
- `strong` - promotion or broad superiority claim where a false positive would matter.

A `strong` claim requires independent replication. Replication must not reuse candidate-mutated evaluator assets or leaked holdout answers.

## Reporting

Report trial count, success/failure/unknown counts, empirical success rate, interval, requested `pass_power`, evaluator identity, stop rule, environment identity when material, and whether independent replication occurred. If execution was not repeated, say so and limit the claim to structural hardening or a single observed run.
