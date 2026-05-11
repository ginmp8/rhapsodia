# Expectations

Input:

- GitHub issue with business impact but incomplete delivery metadata.

Generated artifacts:

- `ops.yaml`
- `status.md`

Validation expectations:

- `validate_ops.py ops.yaml` exits `0`.
- Warnings are expected for missing owner, stakeholders, target date, and priority level.

Warnings:

- Missing fields are intentional because this is intake, not triage.
- Do not add manually maintained branch, review, check, or deployment fields.

Proves:

- nomia can capture GitHub issue intake without inventing governance facts.
- Uncertainty is explicit and traceable.
