# Refresh Impact Analysis

Use only in `refresh` mode.

## Goal

Update a previously traced skill from a changed research corpus without replaying unaffected work.

## Procedure

1. Freeze the new research corpus separately from the prior corpus.
2. Compare source identities and atomic findings.
3. Classify finding delta as `added`, `changed`, `removed`, or `unchanged`.
4. Preserve IDs for semantically unchanged findings; allocate new IDs for genuinely new findings.
5. For changed/removed findings, walk downstream dependencies:

`Finding -> Requirement -> Change + Evaluation`

6. Mark impacted downstream records `invalidated` in the working analysis before reuse.
7. Re-derive only affected requirements.
8. Re-evaluate only affected changes and evaluators plus any shared contract whose semantics may have changed.
9. Run the full final structural trace validator after local repairs.
10. Report both the research delta and implementation delta.

## Invalidation rules

- Source metadata-only changes do not automatically invalidate a finding if claim semantics and authority remain unchanged.
- Finding wording changes that alter qualifiers, scope, version, or uncertainty invalidate derived requirements.
- Requirement semantic changes invalidate linked implementation and evaluations.
- Evaluation-only changes invalidate behavioral comparison evidence but not necessarily implementation bytes.
- A removed finding may leave a requirement valid if other findings independently justify it; update `derived_from` rather than deleting blindly.
