# Expectations

Input:

- A material governance decision that has already been accepted.

Generated artifacts:

- `adr-records.md`

Validation expectations:

- `validate_artifact.py adr-records.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Magnomo records accepted material decisions as append-only ADR records.
- ADR entries preserve context, alternatives, rationale, impact, links, and supersession state.

