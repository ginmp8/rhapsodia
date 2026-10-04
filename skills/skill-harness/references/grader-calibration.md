# Grader Calibration and Bias Controls

Use when a human/model grader materially affects acceptance or promotion. Freezing a grader proves identity stability; calibration tests whether it agrees sufficiently with an accepted reference and resists known presentation biases.

Validate `assets/templates/grader-calibration.json.template` with:

```text
<PYTHON> scripts/validate_grader_calibration.py <CALIBRATION.json>
```

Record grader identity, reference-set identity, agreement sample, abstentions, and explicit thresholds. Include order-swap probes for position bias and verbosity probes when output length could influence preference. The validator derives agreement, coverage, and consistency metrics and fails declared thresholds.

An uncalibrated LLM grader may be auxiliary evidence, but it must not be the sole hard promotion gate for a strong claim. Prefer deterministic outcome checks where possible; use human/expert labels to calibrate subjective graders. Preserve `Unknown`/abstain behavior when evidence is insufficient.
