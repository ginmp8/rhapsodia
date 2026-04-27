# Expectations

Input:

- A material governance proposal that is not decided yet.

Generated artifacts:

- `rfc-proposals.md`

Validation expectations:

- `validate_artifact.py rfc-proposals.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Magnomo records undecided material proposals as RFC entries.
- RFC entries preserve RACI, assumptions, criteria-before-options, and pending outcome without creating implementation tasks.

