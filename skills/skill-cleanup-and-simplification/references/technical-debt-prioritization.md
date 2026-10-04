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

## Priority order

Use this qualitative order unless the user supplies a different scoring rule:

1. Critical blockers: broken links, invalid package structure, unsafe deletion requests, validation failures, or false-removal authority.
2. High-return cleanup: proven generated artifacts, exact duplicates, stale local links, unresolved scaffold with direct evidence.
3. Reachability debt: missing runtime/build/external roots, unresolved dynamic consumers, or incomplete reference evidence.
4. Context-efficiency debt: oversized `SKILL.md`, deep reference chains, duplicated control-plane guidance, or resources loaded earlier than necessary.
5. Maintainability improvements: consolidation, clearer mode boundaries, better templates and reports.
6. Deferred simplification: useful changes that require missing evidence, tests, or domain confirmation.

A simple numeric helper is:

`priority = (impact + risk + confidence) - (6 - ease)`

Higher is more urgent. Safety gates override numeric score.

## Context-efficiency evidence

Use validator/inventory metrics as diagnostics, not deletion authority:

- `skill_md_lines`;
- `skill_md_estimated_tokens`;
- `max_reference_depth_from_skill_md`;
- `reference_edge_count`;
- `root_count`;
- weak generated-candidate count;
- unreferenced `integrable` count.

Crossing a recommended context threshold creates remediation debt; it never proves a file is removable.

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
