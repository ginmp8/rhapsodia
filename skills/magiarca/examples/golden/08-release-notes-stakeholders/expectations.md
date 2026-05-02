# Expectations

Input:

- Release evidence and feature-report context for stakeholder communication.

Generated artifacts:

- `release-notes.md`
- `internal-notes.md`

Validation expectations:

- `validate_reporting.py --mode release-notes --release-notes release-notes.md --internal-notes internal-notes.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Release notes can claim availability only when release evidence exists.
- Stakeholder-facing notes stay separate from internal support guidance.
