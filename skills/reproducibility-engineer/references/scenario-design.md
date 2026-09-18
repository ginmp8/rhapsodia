# Scenario Design

## Purpose

Scenarios turn vague reliability goals into repeated evidence. Keep authoring cases and holdout cases separate when meaningful.

## Groups

### Activation
Prompts that should invoke the skill. Cover realistic wording, not only exact keywords.

### Non-activation
Adjacent tasks the skill should not own. These protect against over-triggering.

### Ambiguous
Prompts where routing, scope, or target identity is uncertain. Verify deterministic clarification, guide behavior, or safe defaults.

### Core behavior
Representative high-value happy paths with realistic files/inputs.

### Edge/failure
Missing inputs, malformed files, conflicting facts, unsupported versions, external failures, partial outputs, and permission limits.

### Regression
One scenario per confirmed generalizable defect. The expected outcome should make recurrence observable.

### Adversarial/anti-cheating
Cases that expose superficial passes, such as:
- deleting required semantic content to satisfy layout;
- lowering thresholds;
- editing fixtures;
- ignoring unsupported fields;
- claiming unexecuted validation;
- accepting stale artifacts.

### Holdout
Cases not consulted during candidate authoring. Use these for stronger robustness claims.

## Scenario record

Recommended fields:

```json
{
  "id": "regression-stale-artifact",
  "group": "regression",
  "prompt": "...",
  "files": [],
  "expected": {
    "activation": true,
    "hard_gates": ["..."],
    "observable": "..."
  }
}
```

## Quality rules

- Scenarios must reflect real usage, not paraphrases of `SKILL.md`.
- Do not write only easy happy paths.
- Do not change holdout/golden expected results because a candidate failed.
- Prefer fewer scenarios that exercise distinct behavior over many near-duplicates.
- For subjective outputs, evaluate specific rubric dimensions rather than one vague "looks good" score.
- Record environment/tool limitations that prevent execution.
