# Expectations

Input:

- Triage notes with owner, stakeholders, target date, and business impact.

Generated artifacts:

- `ops.yaml`
- `stakeholder-brief.md`
- `status.md`

Validation expectations:

- `validate_ops.py ops.yaml` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Triage turns intake into owned delivery metadata.
- Stakeholder communication stays human-facing and does not become Mago task decomposition.
