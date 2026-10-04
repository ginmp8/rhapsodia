# Evaluation Protocol

Evaluate the skill in layers.

## L0 - structure

Validate frontmatter, local references, schemas, eval shape, migration documentation, and package hygiene.

## L1 - deterministic contract

Run `scripts/validate_decision.py` against valid and invalid fixture envelopes. Cover:

- `binary|choice|score` type-specific values;
- Choice option membership, exhaustiveness, and option criteria;
- ordinal and numeric score contracts;
- non-decided null decision values and null confidence;
- confidence/materiality/evidence rules;
- calibration rules;
- `blocked|escalate` next-action rules.

## L2 - focused semantic scenarios

Use `evals/decision-scenarios.json` to test whether a host/model chooses the correct decision type, preserves explicit options/scale/exhaustiveness, uses evidence appropriately, and abstains/escalates when required.

Include metamorphic checks. At minimum, a paired Choice case must preserve the same evidence, criteria, option set, and expected winner while changing option order. Position alone must not change the selection.

When ground truth permits, track selective-decision metrics separately from ordinary decision correctness:

- `decision_coverage`: fraction of eligible cases returned as `decided`;
- `unsafe_decision_rate`: fraction of cases that should abstain/escalate but were forced to `decided`;
- `unnecessary_abstention_rate`: fraction of cases with adequate evidence that were returned non-decided;
- escalation precision/recall when an escalation oracle exists.

Do not optimize coverage alone; a system can appear more decisive by making unsafe forced decisions.

## L3 - adversarial/regression

Include pressure to invent options, fake probabilities, invent criterion weights/thresholds, ignore conflicting evidence, force high-risk decisions, reveal hidden chain-of-thought, or bypass higher-priority policy.

Include invariance/regression cases for semantically irrelevant formatting or ordering when those transformations should not change the result.

## L4 - paired comparison

For an existing version, compare the immutable baseline and candidate with the same scenario/evaluator identities. Separate structural repairs from executed behavioral improvements.

If model/host stochasticity can materially change the claim, run repeated trials. Preserve evaluator identity and material environment/provider/model/tool identities sufficiently to interpret the pair. Report uncertainty/trial counts rather than presenting one run as stable behavior.

## L5 - holdout

Use hidden or author-unseen cases when making strong generalization claims. Do not call bundled visible evals true holdouts.

## Claim rules

- Static schemas/fixtures can prove structural and deterministic contract properties only.
- Bundled planned scenarios do not prove behavioral accuracy, invariance, or reliability until executed.
- One host/model trial does not support a strong stability claim when output is stochastic.
- A better aggregate score never overrides a blocking safety, authority, compatibility, or contract regression.
