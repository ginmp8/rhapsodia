# Finding Model

## Severity

Use the emoji and label together in every material finding.

| Severity | Meaning for skill packages | Default verdict effect |
|---|---|---|
| 🔴 `BLOCKER` | Core activation or execution is impossible, package is invalid, a required resource is missing, the main output contract cannot be satisfied, or a contradiction makes correction unsafe or indeterminate. | `REWORK_REQUIRED` |
| 🟠 `MAJOR` | A common path can activate incorrectly, route incorrectly, produce unreliable output, skip a required gate, rely on a broken validator, or misrepresent evidence. | Usually `REWORK_REQUIRED` |
| 🟡 `MINOR` | Bounded defect, incomplete edge handling, weak calibration, local drift, or maintainability gap that does not break common use alone. | May allow `READY_WITH_COMMENTS` |
| 🔵 `NIT` | Cosmetic naming, formatting, local repetition, or minor clarity issue without behavioral consequence. | No direct effect |
| 🟣 `QUESTION` | Missing or ambiguous evidence that can change severity, score, or verdict. | May cause `NEEDS_MORE_CONTEXT` when essential |

Do not elevate a preference to a defect. Do not downgrade a broken common path because the package has good documentation elsewhere.

## Evidence status

- **Confirmed:** directly supported by inspected content or executed command output.
- **Likely:** multiple strong signals support the defect, but one material confirmation is missing.
- **Needs verification:** plausible and decision-relevant, but insufficient for a finding.
- **Planned:** proposed validation, not current evidence.
- **Out of scope:** relevant surface intentionally not inspected.

## Required finding fields

Each blocker, major, or minor finding must include:

1. **ID:** stable within the report, for example `F-001`.
2. **Severity:** visual label.
3. **Category:** activation, workflow, architecture, consistency, resource, output, validation, documentation, package, or token efficiency.
4. **Evidence status:** confirmed, likely, or needs verification.
5. **Location:** exact file and heading, line range, command, or package surface when available.
6. **Expectation:** the contract or invariant that should hold.
7. **Evidence:** observed content or command result.
8. **Failure path:** how the defect is triggered.
9. **Impact:** concrete consequence for activation, execution, output, validation, maintenance, or packaging.
10. **Root cause:** local defect or architectural cause when supported.
11. **Smallest fix:** minimum sufficient change.
12. **Acceptance criteria:** observable post-fix conditions.
13. **Validation:** exact command, scenario, inspection, or comparison that proves closure.
14. **Correction priority:** required now, recommended, optional, or pending answer.
15. **Dependencies:** other finding IDs or `none`.

Nits may use a compact line. Questions must state what answer would change.

## Finding quality tests

Reject or downgrade a candidate finding when:

- it cites no location or observed behavior;
- it describes only a preferred style;
- the impact is generic rather than tied to the target skill;
- the proposed fix is broader than the defect;
- the validation cannot distinguish fixed from unfixed behavior;
- it assumes an optional resource is mandatory without contract evidence;
- it repeats another finding's root cause without a distinct failure path.

## Compact format

```markdown
### F-001 - 🟠 `MAJOR` - Objective title

- **Category:** Activation
- **Evidence status:** Confirmed
- **Location:** `SKILL.md` > frontmatter description
- **Expectation:** Common review prompts should activate the skill.
- **Evidence:** ...
- **Failure path:** ...
- **Impact:** ...
- **Root cause:** ...
- **Smallest fix:** ...
- **Acceptance criteria:** ...
- **Validation:** ...
- **Correction priority:** Required now
- **Dependencies:** none
```
