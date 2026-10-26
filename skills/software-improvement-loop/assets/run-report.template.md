# Software improvement report

- Experiment: `<id>`
- Objective/mode: `<source-grounded goal>` / `<mode>`
- Scope/permissions: `<allowed and forbidden paths/effects>`
- Baseline identity / candidate identity: `<source identities>`
- Frozen evaluation: `<tests, criteria, environment, workload, guardrails>`
- Attempts used / budget: `<attempts>` / `<maximum>`

## Hypothesis and change

`<what changed, why, and affected files>`

## Actual verification

| Check or metric | Before | After | Evidence and conditions | Result |
|---|---|---|---|---|
| `<name>` | `<value/status>` | `<value/status>` | `<command, path, environment>` | `<pass/fail/not-run>` |

## Decision and recovery

- Decision: `keep | revert | inconclusive | blocked`
- Reason: `<evidence-based conclusion>`
- Preservation of user edits: `<verified / unknown / incomplete>`
- Worktree/branch cleanup: `<status, anything left isolated>`
- Remaining risks / not-run checks: `<explicit>`
- Merge/deployment: `<not requested | authorized and proven action>`
