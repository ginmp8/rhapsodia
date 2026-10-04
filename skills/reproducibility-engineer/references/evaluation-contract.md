# Evaluation Contract

## Contents

- Freeze before mutation
- Freeze source identity
- Environment comparability
- Comparison arms
- Scenario groups and metrics
- Repetition and stochastic reliability
- Acceptance and saturated metrics
- Evaluator independence and claim vocabulary

## Goal

Make candidate acceptance independent from the candidate's own edits and reduce false confidence from one lucky LLM run.

## Freeze before mutation

Freeze all evidence that will decide acceptance:
- prompts/scenarios;
- input files;
- expected outputs/golden fixtures;
- validators/graders;
- scoring configuration and thresholds;
- benchmark scripts;
- package gates.

Use `scripts/freeze_evaluator.py`. If a frozen asset changes, invalidate the comparison.

## Freeze source identity

If external files or repository content materially determine the candidate or the acceptance decision, capture those bytes before analysis and keep their identity separate from the evaluator identity. Use `scripts/snapshot_sources.py` for filesystem evidence when available.

For pinned VCS evidence, prefer immutable object reads tied to the recorded revision rather than a working-tree read. Record repository identity, revision, path, and range. Local replacement refs, dirty files, regenerated outputs, or branch movement must not silently redefine a pinned source.

If the live source changes after capture, either keep evaluating the captured snapshot or intentionally invalidate and re-baseline the experiment. Do not mix before-state evidence from one source version with after-state evidence from another.

## Environment comparability

When provider/model/tool/runtime/dependency/cache/concurrency/locale/timezone state can materially affect an outcome, record the execution profile from `references/environment-provenance.md`. For a paired comparison, validate both profiles and compare their material environment identity before attributing a delta to the candidate. Environment drift makes the pair non-comparable unless the experiment deliberately models that drift or is re-baselined.

## Comparison arms

Use the minimum arms that answer the question:

### Old skill vs candidate
Required for improvement claims about an existing skill.

### No skill vs candidate
Use when the question is whether the skill itself adds value.

### Isolated skill vs full plugin/context
Use when neighboring skills, system context, or plugin packaging may change activation/behavior.

Run the same prompts and files for paired arms.

## Scenario groups

At minimum consider:
- activation;
- non-activation;
- ambiguous routing;
- core happy path;
- edge/failure path;
- regression;
- adversarial/anti-cheating;
- holdout scenarios not used while authoring.

See `references/scenario-design.md`.

## Metrics

Choose metrics tied to observed variance, not vanity scores:

- activation precision/recall;
- output contract pass rate;
- validator pass rate;
- regression failure rate;
- average repair rounds;
- unsupported-claim count;
- manual rework rate;
- token cost;
- wall time;
- package/runtime failure rate;
- paired reviewer wins for subjective output;
- empirical success rate, interval, and `pass^k` for repeated stochastic scenarios when relevant;
- environment drift count and lineage invalidation/replay failures when those profiles apply.

Static maturity is a gate, not a behavioral metric.

## Repetition and stochastic reliability

One run can prove a hard failure but rarely proves reliable improvement. When repeated stochastic behavior is part of the claim, use `references/stochastic-evaluation.md` and validate a trial-evidence artifact with `scripts/validate_execution_evidence.py --kind stochastic`.

For strong claims:
- keep prompts/files and the accepted evaluator fixed between paired arms;
- isolate trial state when independence is part of the claim;
- predeclare the stop rule and trial budget;
- report raw outcomes, uncertainty, and reliability-under-repetition rather than average success alone;
- randomize presentation order for human/judge comparison when possible;
- record ties rather than forcing a winner;
- require independent replication before a strong promotion claim;
- use `scripts/paired_sign_test.py` as an optional simple one-sided paired win/loss check when win/loss is the right metric.

`pass^k` is an independence-model estimate derived from observed success rate, not proof that trials are independent. The default `paired_sign_test.py --min-pairs 12` remains a heuristic power warning, not a universal statistical guarantee.

## Acceptance rule

A candidate may be accepted when:

1. all hard gates pass;
2. frozen evaluator identity is unchanged;
3. no blocking structural/semantic/safety regression exists;
4. material source identities remain the captured versions used by the comparison, or the experiment was explicitly re-baselined;
5. material execution-environment identities are comparable for paired evidence, or environment drift was explicitly modeled/re-baselined;
6. the targeted behavioral metric improves enough to meet the predeclared rule when improvement is claimed;
7. strong stochastic claims satisfy the declared repeated-trial and independent-replication profile;
8. cost/time trade-offs remain within the declared budget;
9. subjective quality has the required independent review.

If behavioral execution is unavailable, the valid claim is "structurally hardened" or "validation-ready", not "behaviorally improved".

## Saturated metrics

When a metric is already near its ceiling, do not optimize against noise. Keep it as a gate and add a non-saturated auxiliary metric such as:
- holdout robustness;
- ambiguous activation;
- repair rounds;
- token cost;
- runtime failures;
- manual rework.

## Evaluator independence

Do not let candidate code modify:
- fixtures;
- expected outputs;
- grader prompts;
- thresholds;
- golden data;
- baseline reports.

If generator and validator must share a library, freeze that shared dependency and add at least one independent end-to-end check.

## Claim vocabulary

Use:
- `measured`: executed command/scenario/evaluator evidence;
- `observed`: direct file/output inspection;
- `derived`: deterministic calculation from evidence;
- `supplied`: user-provided result not independently executed;
- `planned`: not executed;
- `blocked`: could not be obtained.

Never upgrade a weaker label to `measured` for presentation quality.
