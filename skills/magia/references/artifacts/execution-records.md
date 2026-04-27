# Execution Records

Load this reference when execution updates `tasks.md`, `spec-catalog.yaml`, `manifest.yaml`, `validation.md`, or `notes.md`.

## Ownership Boundary

- execution records must live under `BOARD_ROOT`
- `board_id` and `cycle_version` must be concrete dynamic path segments before any record is read or updated
- `prd.md` is an execution input; `tasks.md` is a read-mostly execution input whose existing checkboxes may be updated in place
- do not create, refine, split, resequence, or rewrite tasks during execution
- execution may toggle only the existing checkbox of a task that truthfully reached `done`; do not edit task prose, ids, order, dependencies, or metadata
- if honest execution would require changing the task plan or task metadata, stop and hand off to the planning workflow
- use `assets/templates/tasks.md.template` only through `scripts/write_artifact_scaffold.py` when a canonical execution artifact must be seeded, or as a read-only contract reference after script validation when you need to understand why the input task structure is malformed

## Canonical Structure

- `spec-catalog.yaml`: preserve `schema_version`, `board_id`, `cycle_version`, `board_status`, and the `specs` sequence; within the selected spec preserve `order`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `depends_on_features`, `depends_on_specs`, `status`, and `feature_version`
- `manifest.yaml`: preserve the field set and order, including `schema_version`, identity fields, `status`, `phase`, `board_id`, `cycle_version`, `source_of_truth`, `traceability`, and optional `last_execution` when execution truth exists; canonical `last_execution` keeps `task_id` required and `date`, `summary`, and `files_changed` optional
- `tasks.md`: preserve phase headings, task order, task ids, and task metadata; during execution only toggle existing checkboxes in place for tasks truthfully completed in the current run
- `validation.md`: preserve the H1, `Validation Strategy`, `Validation Scope`, `Performance Validation`, and `Final Verification Checklist`
- `notes.md`: preserve the canonical top-level sections and the `Execution Log` field labels `Status`, `Summary`, `Changes`, `Context Docs`, `Decisions`, `Follow-Ups`, and `Blockers`; use `Status` only from `not_started`, `in_progress`, `blocked`, or `done`, and use `none` when an execution-log field is intentionally empty

## Writing Rules

- when editing `notes.md` or `validation.md`, open and follow `references/markdown-writing.md`
- when a MAGIA artifact must be seeded, refreshed, or normalized from a template, use `scripts/write_artifact_scaffold.py <artifact-path>` or a narrower local script if one exists; do not copy or patch template text manually
- when a MAGIA template-backed list field must be populated, use `scripts/update_template_lists.py <artifact-path> --data <payload.yaml>`; check supported list shapes with `scripts/update_template_lists.py --schema --artifact-name <artifact>` and extend that script first when a needed list shape is unsupported
- preserve canonical headings, front matter keys, field labels, and checklist or execution-log ordering when the file already follows the expected structure
- when writing or refreshing a `notes.md` `Execution Log` subsection and the local script is available, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...` instead of inserting the subsection manually
- `scripts/write_execution_log.py` is the canonical writer because it keeps `## Execution Log` as the last top-level section, removes any stale copy of the same task subsection, and appends the refreshed subsection at EOF
- restore missing required structure conservatively instead of deleting neighboring truthful content
- use local files under `assets/templates/` only through scripts when an execution artifact must be written or validated; read them directly only as contract references after the relevant script cannot perform the check
- never overwrite truthful dynamic values with placeholders or copied example literals
- when task completion state changed truthfully in this run or execution records changed and the local script is available, use `scripts/close_execution_state.py` as the canonical closure step so sync, narrow self-healing, and validation happen together
- fall back to `scripts/sync_execution_state.py <board_root> --spec-id <specNNN> ...` followed by `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` only when `scripts/close_execution_state.py` is unavailable
- use `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` only for narrow mechanical reconciliation already proven by existing `notes.md` and `validation.md` evidence; do not use it to invent validation, rewrite tasks, or repair task ids
- validate touched artifacts with `scripts/validate_artifact.py <artifact-path>` before closure so validator selection is mechanical rather than ad hoc
- run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` before closure when local repository files are available
- when toggling a `tasks.md` checkbox, edit the existing task line in place and keep the surrounding task content untouched
- when toggling a `validation.md` final checklist item, edit the existing list item in place and keep any attached context immediately below it
- update `manifest.yaml.last_execution` only when a real task executed; otherwise preserve the truthful existing value or omit the field

## Cross-Artifact Consistency

- any `taskNNN` referenced by a `notes.md` `Execution Log` subsection or by `manifest.yaml.last_execution.task_id` must exist in `tasks.md`
- any task truthfully completed in the current run must have its existing `tasks.md` checkbox checked in place before closure
- any task recorded as executed in `notes.md` should also have matching `validation.md` evidence before closure
- preserve truthful legacy `last_execution` data unless the current run has better direct evidence
- if `manifest.yaml` or `spec-catalog.yaml` is marked `done`, do not leave required tasks open in `tasks.md`
- do not duplicate execution evidence across noncanonical docs
