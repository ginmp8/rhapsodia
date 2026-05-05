# Reporting Contract

Use this final report shape. Keep measured facts separate from design judgment.

## Required sections

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

## Change Gate
- Policy:
- Candidate gate status:
- Final gate status:
- Blocking regressions:
- Material concerns:
- Accepted trade-offs:

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
- Change-gate status:
- Token delta:
- Final token-efficiency closure:
- Gates:

## Package
- Archive:
- Size:
- Validation:

## Remaining Risks
## Next Recommended Hypothesis
```

## Evidence language

Use `measured` for executed commands/scenario results/validators/package checks, `observed` for file inspection, `inferred` for reasoned conclusions from files, `planned` for unexecuted checks, and `blocked` for missing tools/permissions/safe scope. Do not say `production-ready`, `secure`, `benchmark improved`, or behavioral precision/recall unless corresponding checks passed.

## Pass ledger example

```markdown
| skill-harness | pass | validation report | scenarios valid; execution planned |
| skill-token-efficient | pass | token audit | validation rerun after compression |
| skill-change-gate | pass | gate report or checklist | no blocking regression before accepting candidate |
| final skill-change-gate | pass | final gate report | no blocking regression after hardening/compression |
| final skill-token-efficient closure | pass | audit-only token check | no mutation; no validation rerun required |
```
