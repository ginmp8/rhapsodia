# Technical Debt Prioritization

Use this model for `technical-debt-plan` mode.

## Scores

Score each item from 1 to 5.

| Metric | 1 | 3 | 5 |
|---|---|---|---|
| Ease | Hard, risky, or cross-cutting | Moderate edits | Trivial and isolated |
| Impact | Cosmetic only | Improves maintainability | Blocks reliable use or validation |
| Risk | Negligible if deferred | Causes recurring confusion | High chance of breakage, misuse, or package drift |
| Confidence | Weak signal | Multiple signals | Direct evidence and validation output |

## Priority formula

Use this qualitative order unless the user supplies a different scoring rule:

1. Critical blockers: broken links, invalid package structure, secrets, unsafe deletion requests, or validation failures.
2. High-return cleanup: generated artifacts, unresolved scaffold, duplicate references, stale local links.
3. Maintainability improvements: consolidation, clearer mode boundaries, smaller `SKILL.md`, better templates.
4. Deferred simplification: changes that are useful but require missing evidence, tests, or domain confirmation.

A simple numeric helper is:

`priority = (impact + risk + confidence) - (6 - ease)`

Higher is more urgent. Do not let the score override safety gates.

## Required plan sections

Every remediation item should include:

- overview;
- evidence;
- affected files;
- ease, impact, risk, and confidence;
- prerequisites;
- ordered implementation steps;
- validation method;
- rollback path;
- owner or reviewer, when known;
- blockers or unknowns.
