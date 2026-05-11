# Expectations

Input:

- A material governance decision that has already been accepted.

Generated artifacts:

- `governance decision-records.md`

Validation expectations:

- `validate_artifact.py governance decision-records.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- nomia records accepted material decisions as append-only governance decision records.
- governance decision entries preserve context, alternatives, rationale, impact, links, and supersession state.

