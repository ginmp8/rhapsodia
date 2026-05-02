# Template Integration

Use when choosing, scaffolding, auditing, or normalizing a template-backed Magiarca artifact.

## Rule

Prefer scripts over manual template copying. Templates define shape; writers and validators enforce current contract.

## Writers

- General artifacts: `scripts/write_artifact_scaffold.py <path> [--spec-id specNNN]`.
- Ops: `scripts/write_ops_scaffold.py <path> --spec-id specNNN`.
- RFC entries: `scripts/upsert_rfc_entry.py`.
- Governance decisions: `scripts/append_governance_decision_entry.py` as governance decision writer.
- Mechanical lists: `scripts/update_template_lists.py <path> --data <payload.yaml>`; inspect schema with `scripts/update_template_lists.py --schema --artifact-name <name>`.

## Validators

Run `scripts/validate_artifact.py <path>` after writes. Use narrower validators when required by mode output: `validate_ops.py`, `validate_roadmap.py`, `validate_reporting.py`, `validate_portfolio.py`, `validate_contracts.py`, or `validate_board_paths.py`.

## Manual Edit Boundary

Manual prose edits are allowed inside existing human sections when facts are supplied or marked unknown. Do not hand-select a fresh template shape, invent required metadata, bypass a writer for template-backed creation, or rewrite unsupported mechanical list structures; extend the script instead.
