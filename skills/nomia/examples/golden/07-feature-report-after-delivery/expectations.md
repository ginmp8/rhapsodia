# Expectations

Input:

- Delivery metadata plus Magia summarized execution evidence.

Generated artifacts:

- `feature-report.md`
- `internal-notes.md`

Validation expectations:

- `validate_reporting.py --mode feature-report --feature-report feature-report.md --internal-notes internal-notes.md` exits `0`.
- `validate_contracts.py --feature-map ../06-roadmap-to-spec-handoff-mago/feature-map.yaml --execution-evidence input-magia-execution-evidence.yaml` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- nomia can produce a delivery report from Magia evidence without owning execution records.
- Missing release evidence is stated instead of inferred.
