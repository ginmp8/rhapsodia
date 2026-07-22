# Report Contract

Match the user's language unless explicitly requested otherwise. Keep evidence labels in a consistent vocabulary.

## Full review

```markdown
# Skill Quality Review

## Executive Summary
- Target:
- Mode: `full-review`
- Review type: static judgment | executed validation | mixed
- Verdict: ✅ `READY` | 🟡 `READY_WITH_COMMENTS` | 🔴 `REWORK_REQUIRED` | 🟣 `NEEDS_MORE_CONTEXT`
- Weighted score: n/100
- Score basis:
- Finding counts:
- Correction input status: ready | ready with questions | blocked

## Scope and Evidence
### Reviewed
### Not reviewed
### Assumptions
### Commands executed
| Command/check | Status | Evidence |

## Reconstructed Skill Contract
- Role:
- Activation:
- Non-activation:
- Modes:
- Inputs:
- Outputs:
- Validation:
- Stop conditions:

## Behavioral Invariants
1. ...

## Scorecard
| ID | Dimension | Weight | Raw 0-5 | Weighted | Evidence | Main deduction |
|---|---|---:|---:|---:|---|---|

### Gate Overrides
- ...

## Findings
### F-001 - 🟠 `MAJOR` - ...
Use every required field from `references/finding-model.md`.

## Rejected Hypotheses and Positive Signals
### Rejected hypotheses
### Positive signals

## Validation Gaps
- ...

## Prioritized Remediation Plan
| Order | Finding | Action | Depends on | Closure evidence |

## Correction Input
Use `references/correction-input-contract.md` and place the complete copy-paste-ready input here.

## Final Verdict
- Verdict:
- Why:
- Remaining uncertainty:
- Next review gate:
```

## Quick triage

Limit to the five highest-value findings.

```markdown
## Quick Triage
- Target:
- Scope:
- Verdict:
- Review type:

## Top Findings
1. **🟠 `MAJOR` - Issue:** evidence -> impact -> smallest fix -> validation.

## Gaps
- ...

## Correction Input
- Include a compact copy-paste-ready remediation block when the target is sufficient.
```

## Compare versions

```markdown
# Skill Change Review

## Executive Summary
- Baseline:
- Candidate:
- Verdict: accept | accept with comments | reject | needs more context
- Net quality effect:

## Comparison Evidence
| Surface | Baseline | Candidate | Effect | Evidence status |

## Introduced Regressions
## Resolved Defects
## Unchanged Defects
## Uncertain Differences
## Score Delta
State whether the delta is static judgment or measured evidence.
## Acceptance Decision
## Correction Input
```

Do not infer improvement from fewer files, fewer tokens, or more tests alone. Connect the change to preserved or improved behavior.

## Report validation

```markdown
# Review Report Validation

## Report Under Review
## Verdict
## Missing Required Sections
## Unsupported Claims
## Finding Quality Failures
## Score/Verdict Inconsistencies
## Correction Input Defects
## Minimal Repairs
```

## Evidence language

- `measured`: executed scenario, validator, syntax check, package check, or supplied result.
- `observed`: direct file or report inspection.
- `inferred`: conclusion supported by observed evidence.
- `planned`: not executed.
- `blocked`: unavailable because of scope, access, or missing target.

Do not use `measured` for a checklist score. Do not state that the skill is bug-free, optimal, production-ready, or fully validated unless the declared gates were executed and support that exact claim.
