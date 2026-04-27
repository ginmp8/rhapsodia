# Skill Improvement Report Template

Use this structure for manual, automated, self-improvement, and package/install runs. Mark evidence as measured only when commands or captured scenario outputs actually exist.

```markdown
# Skill Improvement Report: <target>

## Summary

- Target skill: `<target>`
- Mode: `<benchmark-only | manual-patch | automated-loop | package-install | self-improvement>`
- Baseline score: `<score>`
- Final score: `<score>`
- Auxiliary metric: `<metric and result, or not used>`
- Delta: `<delta>`
- Iterations: `<count>`
- Accepted patches: `<count>`
- Rejected patches: `<count>`
- Verdict: `<improved | unchanged | failed | packaged>`

## Evaluator and freeze contract

- Evaluator mode: `<skill-benchmark | hybrid | command | generated-first>`
- Benchmark lock or hash: `<hash/path>`
- Required gates: `<gates>`
- Blocked paths: `<paths>`
- Safety mode: `<manual review | isolated container | ci | disposable sandbox>`

## Accepted hypotheses

| Iteration | Hypothesis | Score before | Score after | Files changed | Rationale |
|---:|---|---:|---:|---|---|

## Rejected hypotheses

| Iteration | Hypothesis | Score before | Score after | Reason rejected |
|---:|---|---:|---:|---|

## Final changed files

```text
<changed file list or diff stat>
```

## Commands executed

```text
<important commands and pass/fail outcome>
```

## Validation and package gates

| Gate | Result | Evidence |
|---|---|---|
| Target validator | `<pass/fail>` | `<command/output>` |
| Hardening validator | `<pass/fail>` | `<command/output>` |
| Package creation | `<pass/fail/not requested>` | `<path>` |
| Blocked paths unchanged | `<pass/fail>` | `<hash or diff evidence>` |

## Risks and follow-ups

1. `<risk or next hypothesis>`
```
