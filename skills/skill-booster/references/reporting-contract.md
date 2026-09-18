# Reporting Contract

Use this final report shape. Omit only sections that are truly not applicable, and state why when omission could be mistaken for an unrun gate.

```markdown
# Skill Booster Optimization Report

## Target
- Skill:
- Path:
- Mode:
- Objective:
- Final artifact:

## Host Compatibility
- Requested hosts:
- Resolved capabilities:
- Python launcher:
- Portable-core validation:
- Host adapter validation:
- Blocked/unavailable capabilities:

## Baseline
- Evaluator:
- Score:
- Gates:
- Frozen inputs:
- Blocked paths:

## Source Integrity
- Snapshot manifest:
- Snapshot identity SHA-256:
- Pinned repository revision/path when applicable:
- Final source verification:
- Re-baselined: yes/no

## Reproducibility Routing
- State: invoke-audit | invoke-apply | not-applicable | blocked | unavailable
- Selected mode: audit-only | apply | none
- Specialist status:
- Downstream owner:
- Material signals:
- Decision validator:
- Reproducibility ceiling/findings when invoked:

## Specialist Pass Ledger
| Pass | Status | Execution type | Evidence | Notes |
|---|---|---|---|---|

## Required Specialist Sequence Reconciliation
- Required specialists:
- Actually invoked:
- Checklist-only:
- Blocked:
- Unavailable:
- Not applicable:
- Not run:
- Full sequence satisfied:
- Finalization allowed:

## Hypothesis Discovery
- Policy:
- Status:
- Generated:
- Selected:
- Deferred:
- No-mutation rationale:

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

## Portability Evidence
| Host/profile | Status | Adapter | Evidence/limitations |
|---|---|---|---|

## Validation Evidence
| Command or check | Status | Output or report |
|---|---|---|

## Final Evaluation
- Evaluator:
- Final score:
- Delta:
- Hypothesis-discovery status:
- Change-gate status:
- Token delta:
- Local token regressions:
- Accepted local token trade-offs:
- Final token-efficiency closure:
- Gates:

## Final Freeze
- Manifest:
- Freeze verification:
- Candidate SHA-256:
- Edited after freeze: yes/no

## Package
- Archive:
- Size:
- Candidate SHA-256:
- Archive SHA-256:
- Receipt version/stage:
- Atomic replace:
- Last-known-good preserved on failure:
- Recovery paths:
- Validation:

## Remaining Risks
## Next Recommended Hypothesis
```

## Evidence language

Use `measured` for executed commands/scenario results/validators/package checks, including portability validators; `observed` for file inspection, `inferred` for reasoned conclusions from files, `planned` for unexecuted checks, and `blocked` for missing tools/permissions/safe scope. Use `invoked-skill` only when the skill was actually invoked; use `checklist-only` for manual application. Do not say `production-ready`, `secure`, `benchmark improved`, `reproducibility-engineer invoked`, `full specialist sequence executed`, or behavioral precision/recall unless corresponding evidence exists.

## Pass ledger example

```markdown
| skill-harness | pass | invoked-skill | validation report | scenarios valid; execution planned |
| reproducibility decision + optional reproducibility-engineer | not-applicable | not-applicable | validated decision JSON | no material controllable variance |
| skill-hypothesis-discovery | pass | invoked-skill | backlog report | top hypotheses selected for improver |
| skill-change-gate | pass | invoked-skill | gate report | no blocking regression before accepting candidate |
| final skill-change-gate | pass | invoked-skill | final gate report | no blocking regression after hardening/compression |
```
