# Integration with Skill Improver

Use this reference when `skill-change-gate` is part of a measured improvement loop.

## Role Split

| Component | Owns |
|---|---|
| `skill-improver` | hypothesis selection, frozen evaluator, baseline score, candidate patch, metric delta, rollback, final experiment report |
| `skill-change-gate` | structural acceptance, regression classification, evidence sufficiency, accept/reject gate impact |
| benchmark or evaluator | measured score, pass/fail gates, scenario metrics, report artifacts |

## Recommended Sequence

```text
1. freeze evaluator and blocked paths
2. measure baseline
3. apply one candidate hypothesis
4. rerun frozen evaluator
5. run skill-change-gate on the candidate
6. accept only if metric improved and change gate passed
7. otherwise reject, revert, or require repair before acceptance
```

## Acceptance Rule for `skill-improver`

Accept a candidate only when all conditions hold:

```text
same evaluator inputs
and required benchmark/evaluator gates pass
and metric improves by configured delta
and blocked paths are unchanged
and skill-change-gate status is pass or explicitly waived pass-with-warnings
```

Fail or hold the candidate when:

- the metric improves but the change gate reports a blocking regression;
- the change gate passes but the metric does not improve;
- evaluator inputs drift;
- required evidence is missing;
- material concerns are unresolved under strict policy.

## Policy Defaults

| `skill-improver` mode | Change gate policy |
|---|---|
| `benchmark-only` | not-run unless the user asks for quality interpretation |
| `manual-patch` | normal |
| `automated-loop` | strict |
| `self-improvement` | strict |
| `package-install` | normal or strict depending on destination risk |

## Report Snippet for Caller

```markdown
quality gate:
- status:
- policy:
- blocking regressions:
- material concerns:
- accepted trade-offs:
- decision impact:
```

## Non-Goals

Do not let this gate select hypotheses, tune the benchmark, change evaluator weights, edit the target, or claim measured improvement. It only decides whether the candidate remains acceptable after the measurement workflow has done its part.
