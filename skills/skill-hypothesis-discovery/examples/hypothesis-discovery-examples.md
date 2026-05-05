# Hypothesis Discovery Examples

## Example 1: saturated benchmark

Input signal:

- static benchmark is 100/100;
- no executed activation or non-activation prompt results;
- `evals/` has only planned scenarios.

Good output:

| id | hypothesis | evidence signal | expected effect | validation | recommendation |
|---|---|---|---|---|---|
| H001 | Add holdout activation prompts | score is saturated without behavioral coverage | turns saturated score into a gate and adds auxiliary evidence | harness scenario schema plus execution when available | gather-evidence |
| H002 | Add adjacent non-activation prompts | no negative prompts are measured | tests activation precision before frontmatter mutation | activation review or prompt suite | test-now |

Decision: gather evidence first if no runner exists; do not rewrite `SKILL.md` merely to chase a saturated score.

## Example 2: weak activation description

Input signal:

- user reports false activations on generic code review prompts;
- frontmatter lacks non-use boundaries.

Good hypothesis:

```text
H001 - Add negative activation boundaries
If the frontmatter description names adjacent non-goals, activation precision should improve because generic code review and repository refactor prompts can be routed away.
Validation: non-activation prompt suite plus no regression on should-activate prompts.
Recommendation: test-now.
```

## Example 3: no mutation recommended

Input signal:

- activation, non-activation, edge, and output-contract scenarios are executed and passing;
- validators and package checks pass;
- token audit shows no avoidable duplication.

Good output:

```text
recommendation: no-mutation-recommended
reason: no high-confidence, measurable, low-risk mutation is visible. next best work is monitoring real failures or adding new holdout prompts from future usage.
```

## Example 4: reject random mutation

Bad hypothesis:

```text
Rename all sections and reorganize references to see whether the score improves.
```

Reject it because there is no observed signal, mechanism, validation method, or bounded rollback plan.
