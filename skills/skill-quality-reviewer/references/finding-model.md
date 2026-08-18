# Finding Model

## Severity

Use the emoji and label together in every material finding.

| Severity | Meaning for skill packages | Default verdict effect |
|---|---|---|
| 🔴 `BLOCKER` | Core activation or execution is impossible, package is invalid, a required resource is missing, the main output contract cannot be satisfied, or a contradiction makes correction unsafe or indeterminate. | `REWORK_REQUIRED` |
| 🟠 `MAJOR` | A common path can activate incorrectly, route incorrectly, produce unreliable output, preserve obsolete compatibility, transfer authority, skip a required gate, rely on a broken validator, or misrepresent evidence. | Usually `REWORK_REQUIRED` |
| 🟡 `MINOR` | Bounded defect, incomplete edge handling, weak calibration, local legacy residue, drift, or maintainability gap that does not break common use alone. | May allow `READY_WITH_COMMENTS` |
| 🔵 `NIT` | Cosmetic naming, formatting, local repetition, or minor clarity issue without behavioral consequence. | No direct effect |
| 🟣 `QUESTION` | Missing or ambiguous evidence that can change severity, classification, score, removal safety, or verdict. | May cause `NEEDS_MORE_CONTEXT` when essential |

Do not elevate a preference or keyword match to a defect. Do not downgrade a broken common path because the package has good documentation elsewhere.

## Evidence status

- **Confirmed:** directly supported by inspected content or executed command output.
- **Likely:** multiple strong signals support the defect, but one material confirmation is missing.
- **Needs verification:** plausible and decision-relevant, but insufficient for a finding.
- **Planned:** proposed validation, not current evidence.
- **Out of scope:** relevant surface intentionally not inspected.

## Legacy classification

For legacy, compatibility, migration, ownership, or structural-noise findings, include exactly one classification from:

- `current`;
- `migration-only`;
- `obsolete`;
- `duplicate`;
- `contradictory`;
- `noise`;
- `blocked`.

A legacy classification is not a severity. For example, an `obsolete` unused comment may be a `MINOR`, while a `contradictory` normal-path handoff can be a `MAJOR` or `BLOCKER`.

Use `blocked` when removal or preservation depends on missing owner, consumer, version, migration, or compatibility evidence. State exactly what evidence resolves it.

## Required finding fields

Each blocker, major, or minor finding must include:

1. **ID:** stable within the report, for example `F-001`.
2. **Severity:** visual label.
3. **Category:** activation, workflow, architecture, consistency, resource, output, validation, documentation, package, token efficiency, legacy, compatibility, migration, ownership, runtime coupling, or structural noise.
4. **Evidence status:** confirmed, likely, or needs verification.
5. **Location:** exact file and heading, line range, command, or package surface when available.
6. **Expectation:** the contract or invariant that should hold.
7. **Evidence:** observed content or command result.
8. **Failure path:** how the defect is triggered or how the residue affects maintenance and current behavior.
9. **Impact:** concrete consequence for activation, execution, authority, output, compatibility, validation, maintenance, or packaging.
10. **Root cause:** local defect or architectural cause when supported.
11. **Smallest fix:** minimum sufficient change.
12. **Acceptance criteria:** observable post-fix conditions.
13. **Validation:** exact command, scenario, inspection, rejection test, or comparison that proves closure.
14. **Correction priority:** required now, recommended, optional, or pending answer.
15. **Dependencies:** other finding IDs or `none`.
16. **Legacy classification:** required only for legacy, compatibility, migration, ownership, runtime-coupling, or structural-noise findings.
17. **Canonical source:** required for those same categories when a current replacement or owner exists; otherwise state `unresolved`.

Nits may use a compact line. Questions must state what answer would change. A `blocked` candidate should usually be a `QUESTION` unless the missing evidence itself violates a required gate.

## Finding quality tests

Reject or downgrade a candidate finding when:

- it cites no location or observed behavior;
- it describes only a preferred style;
- it was inferred only from words such as `legacy`, `previously`, `v1`, or `fallback`;
- the impact is generic rather than tied to the target skill;
- the proposed fix is broader than the defect;
- the validation cannot distinguish fixed from unfixed behavior;
- it assumes an optional resource is mandatory without contract evidence;
- it recommends deletion without checking writers, consumers, imports, links, tests, packaging, and migration support;
- it repeats another finding's root cause without a distinct failure path.

## Compact format

```markdown
### F-001 - 🟠 `MAJOR` - Objective title

- **Severity:** 🟠 `MAJOR`
- **Category:** Compatibility
- **Evidence status:** Confirmed
- **Legacy classification:** Obsolete
- **Canonical source:** `references/contracts/handoff-v2.schema.json`
- **Location:** `scripts/validate_handoff.py:44-71`
- **Expectation:** The normal path accepts only the current handoff contract.
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
