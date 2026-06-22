# Output Contracts

Use these shapes unless the user requests a different format. Keep answers in English unless the user explicitly requests another language for the final response.

## Quick triage

Use this compact contract when the user asks for a short review, quick check, first-pass scan, or small snippet triage. Keep it concise: no full PR template unless the user requests a full review.

```markdown
## Quick triage
- Scope reviewed:
- Assumptions:
- Verdict: ✅ `APPROVED` | 🟡 `APPROVED_WITH_COMMENTS` | 🔴 `CHANGES_REQUESTED` | 🟣 `NEEDS_MORE_CONTEXT`

## Top findings
1. **🔴 `BLOCKER`/🟠 `MAJOR`/🟡 `MINOR`/🔵 `NIT`/🟣 `QUESTION` - Issue:** evidence -> impact -> smallest fix -> validation.

## Gaps
- ...

## Next check
- ...
```

Rules: list at most three top findings unless a severe secret, authz, data-loss, contract, or production-failure risk needs expansion. Do not omit evidence labels. Do not approve when essential context is missing.

## PR risk review

Use this contract for pull requests, diffs, merge checklists, approval requests, and suggested PR comments. Keep answers in English unless the user explicitly asks for another language.

### Severity legend

Use the emoji and label together in every finding and suggested PR comment:

- 🔴 `BLOCKER`: blocks merge; critical/high risk, probable production failure, real/probable secret exposure, authz bypass, tenant/data isolation break, data loss, broken contract, unsafe destructive migration, duplicate financial/legal side effect, or irreversible rollback risk.
- 🟠 `MAJOR`: should be fixed before merge unless explicitly accepted by the team; relevant technical/security/operational risk.
- 🟡 `MINOR`: recommended non-blocking improvement or bounded risk.
- 🔵 `NIT`: small readability, style, naming, formatting, or consistency issue only.
- 🟣 `QUESTION`: approval-relevant missing context or suspicious but unconfirmed signal.

Security confidence values: `Confirmed`, `Likely`, `Needs verification`, `Not applicable`.

Expected treatment values: `Fix in this PR`, `Already fixed by the author in this PR`, `Accepted by the team without change`, `Future issue opened for follow-up`, `Not applicable`.

### Required format

```markdown
# Pull Request Review

## Executive summary
- PR reviewed:
- Apparent objective:
- Verdict: ✅ `APPROVED` | 🟡 `APPROVED_WITH_COMMENTS` | 🔴 `CHANGES_REQUESTED` | 🟣 `NEEDS_MORE_CONTEXT`
- Overall risk: Critical | High | Medium | Low | Unknown
- Security posture: no issue found in inspected diff | issues found | not enough evidence
- Finding counts:
  - 🔴 Blockers:
  - 🟠 Major:
  - 🟡 Minor:
  - 🔵 Nit:
  - 🟣 Questions:
- Treatment summary:
  - Fix in this PR:
  - Already fixed by the author:
  - Accepted by the team:
  - Future issue opened:
  - Pending without decision:

## Verdict
Choose exactly one: ✅ `APPROVED`, 🟡 `APPROVED_WITH_COMMENTS`, 🔴 `CHANGES_REQUESTED`, or 🟣 `NEEDS_MORE_CONTEXT`.
Explain the reason in up to five lines.

## Scope and assumptions
- Reviewed:
- Assumptions:
- Out of scope / uninspected:

## Main risks
List the highest-impact risks first.

## Security summary
State whether the inspected change shows exposed secrets or credentials, sensitive logs, authn/authz risks, injection risks, CI/CD/infrastructure/configuration risks, or changes requiring rotation, revocation, repository-history audit, build-artifact audit, or log audit. Mask sensitive evidence.

## Findings

### 1. 🔴 `BLOCKER` - Objective title

**File/line:** `path/to/file.ext:Lx-Ly`

**Security confidence:** Confirmed/Likely/Needs verification/Not applicable

**Evidence:**
Describe the observed code/config/diff/log behavior. Do not copy full secrets or sensitive values; use masked evidence such as `Bearer sk_***`, `Password=***`, or `-----BEGIN PRIVATE KEY-----`.

**Problem:**
Explain the incorrect, fragile, unsafe, or risky behavior.

**Impact:**
Explain the concrete functional, technical, operational, data, contract, or security impact.

**Suggestion:**
State the smallest sufficient fix or mitigation.

**Validation:**
State the test, check, scan, replay, migration validation, or manual evidence needed to prove the fix.

**Blocks merge:** Yes/No/Unknown until verified

**Expected treatment:**
- [ ] Fix in this PR
- [ ] Already fixed by the author in this PR
- [ ] Accepted by the team without change
- [ ] Future issue opened for follow-up
- [ ] Not applicable

**Future issue, if applicable:** `link/id or none`

**Treatment note:**
Briefly explain why the item must be resolved now, may be deferred, or was accepted as risk.

---

## Test and validation gaps
List missing or unevidenced unit, integration, contract, authorization, invalid-input, regression, migration, performance, secret scanning, dependency scanning, SAST, or sensitive-log validations.

## Questions for the author
List only questions that can change the approval decision.

## Suggested PR comments
Group concise ready-to-post comments by file. Use the same severity emoji and label. Do not include full secrets or sensitive values.

### `path/to/file.ext`
```md
🔴 `BLOCKER` - The value appears to include a real credential. Remove it, rotate/revoke it, audit logs/history/build artifacts, and replace it with a secret manager or managed identity.
```

## Security remediation
If there are security findings, organize remediation under immediate response, code/configuration fix, and prevention. If there are no security findings, write: `No specific security remediation identified from the inspected diff.`

## Positive signals
List good decisions found in the PR, if any.

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

### Verdict rules

- ✅ `APPROVED`: no relevant findings and validation is adequate for the inspected risk.
- 🟡 `APPROVED_WITH_COMMENTS`: only 🟡 `MINOR`, 🔵 `NIT`, or explicitly accepted non-blocking items remain.
- 🔴 `CHANGES_REQUESTED`: at least one 🔴 `BLOCKER` or unresolved 🟠 `MAJOR` must be fixed before merge.
- 🟣 `NEEDS_MORE_CONTEXT`: essential context is missing for security, correctness, contract, database, or operational impact.

Never use ✅ `APPROVED` when there is a 🔴 `BLOCKER`, probable or confirmed real secret exposure, relevant data loss risk, untreated breaking contract, essential missing context, or high security risk without mitigation.

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
- **🔴 `BLOCKER`/🟠 `MAJOR`/🟡 `MINOR`/🔵 `NIT`/🟣 `QUESTION` - Issue:** evidence -> impact -> smallest fix -> validation.
```
