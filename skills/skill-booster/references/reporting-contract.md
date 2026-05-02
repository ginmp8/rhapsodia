# Reporting Contract

Use this structure for final reports. Keep measured facts separate from design judgment.

## Required Sections

```markdown
# Skill Booster Optimization Report

## Target
- Skill:
- Path:
- Mode:
- Final artifact:

## Objective
- Primary:
- Secondary:
- Assumptions:

## Baseline
- Evaluator:
- Score:
- Gates:
- Main findings:
- Frozen inputs:
- Blocked paths:

## Specialist Pass Ledger
| Pass | Status | Evidence | Notes |
|---|---|---|---|

## Hypotheses
### Accepted
- H1: ...

### Rejected or Blocked
- H2: ...

## Changes Applied
- `SKILL.md`:
- `references/`:
- `scripts/`:
- `assets/templates/`:
- `examples/`:
- `evals/`:
- package/validation:

## Validation Evidence
| Command or check | Status | Output or report |
|---|---|---|

## Final Evaluation
- Evaluator:
- Final score:
- Delta:
- Token delta:
- Gates:

## Package
- Archive:
- Size:
- Validation:

## Remaining Risks
- ...

## Next Recommended Hypothesis
- ...
```

## Evidence Language

Use:

- `measured` for executed commands, scenario runs, validator outputs, or supplied reports;
- `observed` for direct file inspection;
- `inferred` for reasoned conclusions from inspected files;
- `planned` for scenarios or checks not executed;
- `blocked` for checks prevented by missing tools, permissions, or unsafe scope.

Do not use:

- `proved` when only static review was done;
- `production-ready` when package validation failed;
- `benchmark improved` without before/after results;
- `secure` when only a light review was performed.

## Pass Ledger Template

```markdown
| skill-creator-juiced | applied-by-checklist | redesign escalation checked | ordinary optimization kept |
| skill-improver | pass | baseline/final recorded | accepted H1, rejected H2 |
| skill-benchmark | planned | no executable benchmark available | static gates used |
| skill-harness | pass | scenarios/evals/activation.json | 12 planned scenarios |
| skill-token-efficient | pass | token audit delta -18% | validation rerun after compression |
```
