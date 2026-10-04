# Evaluator and Calibration

## Principle

Perceptual review is judgment-bearing evidence. Make the judgment inspectable and bounded; do not pretend that a model or human reviewer is deterministic.

## Default review shape

Prefer criterion-by-criterion pair comparison of reference and candidate over an unstructured global similarity score. Require observable evidence for material findings.

For routine gates, one qualified review can be sufficient when the frozen policy says `required_trials=1` and agreement is not required. Do not add repeated trials merely for ceremony.

## When to require stronger evidence

Increase the evaluator protocol before review when one or more are true:

- the decision is high impact or expensive to reverse;
- prior runs show unstable judgments near the threshold;
- subtle semantic differences are easy to miss;
- prompt/text cues could bias interpretation of the pixels;
- the candidate was optimized directly against the same judge;
- disagreement between reviewers materially changes promotion.

Possible controls:

- `required_trials > 1`;
- `require_agreement=true`;
- independent human/model or model/model review;
- presentation-order swap for pairwise review;
- human adjudication for unresolved disagreement.

The portable core never requires a particular vendor/model or ensemble.

## Uncertainty

Use confidence as evidence quality, not style. If a required criterion falls below `gate_policy.minimum_confidence`, do not force pass/fail. Follow the frozen `low_confidence_action`, normally `inconclusive`.

When agreement is required, `disagreement` follows the frozen policy, normally `inconclusive`. Record why reviewers disagreed when known; do not silently average scores.

## Calibration

Calibration is useful when the reviewer itself becomes a long-lived gate. Use a frozen set of representative and adversarial cases containing at least:

- harmless rendering differences;
- tiny but semantically critical changes;
- large but explicitly allowed changes;
- state/capture mismatch;
- low-confidence cases;
- chart encoding errors when charts are in scope;
- relationship errors when diagrams are in scope.

Compare reviewer decisions to a trusted adjudicated reference when available. Track disagreement/error by criterion, not only a single aggregate score. Recalibrate after evaluator/prompt/model/rubric changes that can affect decisions.

A calibration result supports only the tested evaluator/rubric/case distribution. Do not claim universal perceptual accuracy.

## Anti-bias controls

- Do not tell the reviewer which candidate is expected to pass.
- Keep acceptance thresholds out of free-form visual reasoning when they can be applied deterministically afterward.
- When order effects are material, review both presentation orders and record `order_swap_performed=true`.
- Keep textual metadata from substituting for visual evidence. A plausible description does not override what is visible.
- Separate generator and acceptance reviewer when overfitting/self-approval risk is material.
