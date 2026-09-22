# Evaluation Protocol

Evaluate the skill in layers.

## L0 - structure

Validate frontmatter, local references, schemas, eval shape, and package hygiene.

## L1 - deterministic contract

Run `scripts/validate_decision.py` against valid and invalid fixture envelopes. Cover type-specific values, option membership, score bounds, non-decided null values, confidence rules, materiality, and calibration rules.

## L2 - focused semantic scenarios

Use `evals/decision-scenarios.json` to test whether a host/model chooses the correct decision type, preserves explicit options/scale, uses evidence appropriately, and abstains/escalates when required.

## L3 - adversarial/regression

Include prompt pressure to invent options, fake probabilities, ignore conflicting evidence, force high-risk decisions, reveal hidden chain-of-thought, or bypass higher-priority policy.

## L4 - paired comparison

For an existing version, compare the immutable baseline and candidate with the same scenario/evaluator identities. Separate structural improvements from executed behavioral improvements.

## L5 - holdout

Use hidden or author-unseen cases when making strong generalization claims. Do not call bundled visible evals true holdouts.

Repeat stochastic host/model scenarios when stability claims matter. Never infer behavioral pass rates from static files alone.
