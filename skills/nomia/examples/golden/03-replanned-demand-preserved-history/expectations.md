# Expectations

Input:

- Existing delivery metadata plus a material scope and date change.

Generated artifacts:

- `ops.yaml`
- `replanning.md`
- `status.md`

Validation expectations:

- `validate_ops.py ops.yaml` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Current delivery state can change without deleting historical context.
- `ops.yaml.replanning` and `replanning.md` carry the same material decision.
