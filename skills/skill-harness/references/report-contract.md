# Report Contract

Use this reference when preparing final responses or durable reports for a skill-harness run.

## Required Sections

1. Mode and target.
2. Decision statement.
3. Evidence policy and sources used.
4. Baseline inventory.
5. Baseline audit score and gates.
6. Harness plan with hypotheses, scenarios, metrics, evaluators, and gates.
7. Changes made or proposed.
8. Validation commands and outcomes.
9. Before/after comparison.
10. Auxiliary metrics when the static score is saturated.
11. Residual risks and assumptions.
12. Final recommendation.
13. Package or artifact path when produced.

## Evidence Wording

Use these labels:

- `measured`: a command, test, validator, package operation, or scenario was actually executed.
- `derived`: inferred from target files or supplied context.
- `researched`: supported by cited research sources.
- `proposed`: planned but not executed.
- `unknown`: not available from allowed evidence.

Do not label scenario pass rates, activation precision, recall, or behavioral conformance as measured unless prompts were executed and evaluator results were captured.

## File Change Summary

Group changes by:

- `SKILL.md`
- `references/`
- `scripts/`
- `assets/templates/`
- `examples/evals/`
- `agents/`
- `packaging`

## Command Outcome Format

For each command, report:

```text
PASS|FAIL|SKIPPED — <command or validator name>: <evidence path or concise result>
```

When an intended command cannot run, state the failure and any workaround separately. Do not convert a failed command into a pass because another command produced related evidence.

## Final Recommendation Format

Use one of:

```text
accept: <reason>
```

```text
accept with risks: <reason and residual risks>
```

```text
reject: <blocking gate failures>
```

```text
plan only: <what is ready and what remains>
```

A package path may be returned only when the file exists and the packaging report indicates success.
