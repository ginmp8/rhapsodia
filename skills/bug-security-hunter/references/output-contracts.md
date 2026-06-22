# Output Contracts

Use these shapes unless the user requests a different format. Keep answers in English unless the user explicitly requests another language for the final response.

## PR risk review

```markdown
# Pull Request Risk Review

## Executive summary
- Reviewed: PR/diff/files inspected
- Apparent objective: ...
- Verdict: Approved | Approved with reservations | Blocked | Needs more context
- Overall risk: Critical | High | Medium | Low | Unknown
- Security posture: no issue found in inspected diff | issues found | not enough evidence
- Finding counts: critical/high/medium/low/needs verification
- Treatment summary: fix in this PR | already fixed | accepted risk | future issue | pending

## Scope and assumptions
- Reviewed: ...
- Assumptions: ...
- Out of scope: ...

## Main risks
- ...

## Security summary
State whether the inspected change shows exposed secrets, sensitive logs, authn/authz risk, injection risk, CI/CD or infrastructure risk, or need for rotation/revocation/audit. Mask sensitive evidence.

## Findings
1. [severity] Title
   - File/line: `path/to/file.ext:Lx-Ly` when available
   - Evidence label: confirmed | likely | needs verification | planned | out of scope
   - Evidence: file/path/function/diff/config/log signal
   - Impact: concrete bug/security/reliability outcome
   - Smallest fix: minimal change or mitigation
   - Validation: test/check to prove the fix
   - Blocks merge: yes | no | unknown until verified
   - Expected treatment: fix in this PR | already fixed | accepted risk | future issue | not applicable
   - Future issue, if applicable: id/link or none

## Test and validation gaps
- unit, integration, contract, authorization, invalid input, regression, migration, performance, secret scanning, dependency scanning, SAST, or sensitive-log validation gaps

## Questions for the author
- Only questions that change the approval decision.

## Suggested PR comments
- `path/to/file.ext`: [severity] concise comment ready to post

## Security remediation
- Immediate response: ...
- Code/config cleanup: ...
- Prevention: ...

## Positive signals
- ...

## Final checklist
- [ ] Scope understood
- [ ] Main risks evaluated
- [ ] Tests/validation reviewed
- [ ] Security reviewed
- [ ] Secrets and credentials reviewed
- [ ] Logs/traces/errors reviewed
- [ ] Authentication and authorization reviewed
- [ ] Input validation and injection reviewed
- [ ] CI/CD, configuration, and infrastructure reviewed when applicable
- [ ] Performance reviewed
- [ ] Observability reviewed
- [ ] Operational reliability reviewed
- [ ] Contracts/APIs reviewed when applicable
- [ ] Database/migrations reviewed when applicable
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
- immediate response
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
