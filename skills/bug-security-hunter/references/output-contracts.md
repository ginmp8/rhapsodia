# Output Contracts

Use these shapes unless the user requests a different format.

## PR risk review

```markdown
## Scope
- Reviewed: ...
- Assumptions: ...

## Findings
1. [severity] Title
   - Evidence: file/path/function/diff signal
   - Impact: concrete bug/security/reliability outcome
   - Smallest fix: minimal change
   - Validation: test/check to prove fix

## Validation gaps
- ...

## Merge verdict
Blocked | Approve with reservations | Approve

## Next step
- One concrete action
```

## Flow bug/security hunt

```markdown
## Scope and assumptions
...

## Causal map
| Step | Event/command | Handler/consumer | Side effect | Next event | Risk |
|---|---|---|---|---|---|

## Invariants
- ...

## Findings and risks
1. [severity] ...

## Stress matrix
| Scenario | Hypothesis | Expected proof | Status |
|---|---|---|---|

## Coverage gaps
- ...

## Closure criteria
- ...
```

## Project-wide audit

```markdown
## Audit scope
...

## Hotspot map
| Area | Risk | Why inspect first | Evidence needed |
|---|---|---|---|

## Findings
...

## Recommended audit sequence
1. ...
```

## Security threat review

```markdown
## Assets and trust boundaries
...

## Abuse cases
| Abuse case | Control expected | Evidence | Status |
|---|---|---|---|

## Security findings
...

## Remediation checklist
- immediate containment
- code/config cleanup
- rotation/revocation when applicable
- preventive guardrails
```

## Harness design

```markdown
## Harness goal
...

## Baseline
...

## Scenarios
| ID | Hypothesis | Input/fault | Assertions | Evidence |
|---|---|---|---|---|

## Execution safety
...

## Pass/fail gates
...
```

## Finding line format

Use this compact form for short answers:

```markdown
- **[severity] Issue:** evidence -> impact -> smallest fix -> validation.
```
