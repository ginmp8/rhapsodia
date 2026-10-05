# Code Archaeology

## Purpose
Explain why code exists or how it evolved without confusing historical intent with current behavior.

## Evidence sequence
1. Resolve the current lines/symbols and read their present implementation first.
2. Identify relevant commits with blame/history/log or equivalent repository evidence.
3. Inspect PRs/issues/ADRs/commit messages/traces only when available and authorized.
4. Treat search results as candidate locators; inspect the underlying record before using it as evidence.
5. Build the minimum provenance chain needed to answer the question.
6. Re-read current code after historical investigation and state whether the historical rationale still matches, partially matches, or was superseded.

## Claim rules
- `historical`: directly supported by a commit, PR, issue, ADR, or trace event.
- `observed`: directly supported by current source/config/schema/tests/runtime evidence.
- `inferred`: architectural/rationale interpretation from evidence without an explicit decision record.
- Never attribute motive to a person/agent from code shape alone.
- Missing provenance remains missing; report uncertainty instead of filling the gap.

## Visuals
Use a timeline when multiple events/revisions materially explain evolution. For one historical event, prefer concise prose plus current-state evidence. A provenance chain may connect `requirement/issue -> decision/PR -> commit -> current code`, but only include nodes supported by evidence.
