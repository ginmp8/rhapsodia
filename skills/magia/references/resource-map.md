# Resource Map

Use this reference to locate MAGIA resources without loading every file.

## Core References

- [common-execution.md](common-execution.md): shared execution rules.
- [senior-engineering-discipline.md](senior-engineering-discipline.md): small, explicit, verifiable engineering behavior.
- [complexity-reduction-execution.md](complexity-reduction-execution.md): behavior-preserving simplification, de-abstraction, and refactoring execution.
- [planning-handoff.md](planning-handoff.md): how to consume Mago/Magnomo artifacts as execution inputs.
- [developer-artifact-standards.md](developer-artifact-standards.md): implementation documentation taxonomy and templates.
- [technical-documentation.md](technical-documentation.md): implementation ADR and documentation rules.
- [validation-and-closure.md](validation-and-closure.md): truthful validation and closure.
- [markdown-writing.md](markdown-writing.md): durable Markdown quality.
- [package-delivery.md](package-delivery.md): packaging MAGIA itself.

## Mode References

- [modes/adhoc.md](modes/adhoc.md): direct repository work.
- [modes/ralph.md](modes/ralph.md): execution from selected board/spec packages.

## Artifact References

- [artifacts/execution-records.md](artifacts/execution-records.md): controlled state synchronization.
- [artifacts/execution-evidence.md](artifacts/execution-evidence.md): structured downstream evidence.

## Templates

Core execution templates:

- [../assets/templates/spec-catalog.yaml.template](../assets/templates/spec-catalog.yaml.template)
- [../assets/templates/manifest.yaml.template](../assets/templates/manifest.yaml.template)
- [../assets/templates/tasks.md.template](../assets/templates/tasks.md.template)
- [../assets/templates/notes.md.template](../assets/templates/notes.md.template)
- [../assets/templates/validation.md.template](../assets/templates/validation.md.template)

Developer documentation templates:

- [../assets/templates/implementation-notes.md.template](../assets/templates/implementation-notes.md.template)
- [../assets/templates/complexity-reduction-evidence.md.template](../assets/templates/complexity-reduction-evidence.md.template)
- [../assets/templates/implementation-adr.md.template](../assets/templates/implementation-adr.md.template)
- [../assets/templates/validation-evidence.md.template](../assets/templates/validation-evidence.md.template)
- [../assets/templates/runbook.md.template](../assets/templates/runbook.md.template)
- [../assets/templates/migration-execution-note.md.template](../assets/templates/migration-execution-note.md.template)
- [../assets/templates/contract-change-note.md.template](../assets/templates/contract-change-note.md.template)
- [../assets/templates/observability-note.md.template](../assets/templates/observability-note.md.template)
- [../assets/templates/troubleshooting.md.template](../assets/templates/troubleshooting.md.template)
- [../assets/templates/security-risk-note.md.template](../assets/templates/security-risk-note.md.template)
- [../assets/templates/technical-gap-note.md.template](../assets/templates/technical-gap-note.md.template)

## Scripts

- `scripts/write_artifact_scaffold.py`: copy a matching template to a destination path.
- `scripts/update_template_lists.py`: populate supported template list fields.
- `scripts/write_execution_log.py`: write execution log entries.
- `scripts/sync_execution_state.py`, `scripts/heal_execution_state.py`, `scripts/close_execution_state.py`: synchronize controlled execution records.
- `scripts/validate_artifact.py`, `scripts/validate_execution_state.py`, `scripts/validate_repo_board.py`, `scripts/validate_boundary.py`: validate artifacts and boundaries.
- `scripts/validate_skill_package.py`, `scripts/package_skill.py`: validate and package MAGIA itself.

