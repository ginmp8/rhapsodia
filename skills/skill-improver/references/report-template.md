# Skill Improvement Report Template

Use for manual, automated, self-improvement, and package/install runs. Mark evidence as measured only when commands or captured scenario outputs exist.

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
- Hypothesis source: `<supplied | discovery-backlog | built-in-catalog | fallback>`
- Discovery result: `<not-run | candidates/top/deferred | gather-evidence | no-mutation-recommended>`
- Accepted patches: `<count>`
- Rejected patches: `<count>`
- Verdict: `<improved | unchanged | failed | packaged>`

## Evaluator and freeze contract
- Evaluator mode: `<skill-benchmark | hybrid | command | generated-first>`
- Benchmark lock or hash: `<hash/path>`
- Required gates: `<gates>`
- Blocked paths: `<paths>`
- Safety mode: `<manual review | isolated container | ci | disposable sandbox>`

## Hypothesis discovery
- Backlog source: `<path/report/not-run>`
- Candidates generated: `<count>`
- Top hypotheses selected: `<ids>`
- Deferred hypotheses: `<ids/reasons>`
- Selection rationale: `<why this hypothesis was tested first>`

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

## Structural change gate
- Policy: `<disabled | advisory | required>`
- Status: `<pass | pass-with-warnings | fail | not-run>`
- Blocking regressions: `<none or list>`
- Material concerns: `<none or list>`
- Accepted trade-offs: `<none or list>`
- Decision impact: `<accepted | rejected | advisory only>`

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
