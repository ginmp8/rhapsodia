# Resource Map

Use to locate MAGIA resources without loading every file.

## Core References

- `references/common-execution.md`: shared execution rules.
- `references/senior-engineering-discipline.md`: small, explicit, verifiable engineering behavior.
- `references/complexity-reduction-execution.md`: behavior-preserving simplification, de-abstraction, refactor execution.
- `references/planning-handoff.md`: consume Mago/nomia artifacts, including execution-handoff-plan.md, as execution inputs.
- `references/developer-artifact-standards.md`: implementation-doc taxonomy/templates.
- `references/technical-documentation.md`: implementation ADR and doc rules.
- `references/validation-and-closure.md`: truthful validation/closure.
- `references/markdown-writing.md`: durable Markdown quality.
- `references/package-delivery.md`: package MAGIA itself.

## Mode References

- `references/modes/adhoc.md`: direct repository work.
- `references/modes/ralph.md`: selected board/spec package execution.
- `references/modes/adapt.md`: best-effort conversion of legacy execution records into current MAGIA-owned artifacts.

## Artifact References

- `references/artifacts/execution-records.md`: controlled state sync.
- `references/artifacts/execution-evidence.md`: structured downstream evidence.

## Templates

MAGIA-owned execution evidence templates: `assets/templates/implementation-notes.md.template`, `assets/templates/validation-evidence.md.template`, and `assets/templates/technical-gap-note.md.template`. MAGIA intentionally does not bundle templates for MAGO-owned planning artifacts (`spec-catalog.yaml`, `manifest.yaml`, `tasks.md`, `notes.md`, or `validation.md`). Use MAGO to create or normalize those files, then use MAGIA execution-state scripts only to update existing records from truthful execution evidence.

Developer docs: `assets/templates/implementation-notes.md.template`, `assets/templates/complexity-reduction-evidence.md.template`, `assets/templates/implementation-adr.md.template`, `assets/templates/validation-evidence.md.template`, `assets/templates/runbook.md.template`, `assets/templates/migration-execution-note.md.template`, `assets/templates/contract-change-note.md.template`, `assets/templates/observability-note.md.template`, `assets/templates/troubleshooting.md.template`, `assets/templates/security-risk-note.md.template`, `assets/templates/technical-gap-note.md.template`.

## Scripts

- `scripts/write_artifact_scaffold.py`: copy matching MAGIA-owned template only; it must not scaffold or update MAGO-owned planning files.
- `scripts/write_execution_log.py`: write execution logs.
- `scripts/adapt_legacy_execution_records.py`: convert legacy notes.md/validation.md execution content into current MAGIA-owned artifacts.
- `scripts/sync_execution_state.py`, `scripts/heal_execution_state.py`, `scripts/close_execution_state.py`: sync controlled execution records.
- `scripts/validate_artifact.py`, `scripts/validate_execution_state.py`, `scripts/validate_repo_board.py`, `scripts/validate_boundary.py`: validate artifacts/boundaries.
- `scripts/validate_planning_handoff_contract.py`: validate planning-origin execution and blocker rules after handoff-rule edits.
- `scripts/magia_utils.py`: import-only helper module used by execution-state, boundary, board, and log scripts; it has no standalone CLI by design.
- `scripts/validate_skill_package.py`, `scripts/package_skill.py`: validate/package MAGIA.
