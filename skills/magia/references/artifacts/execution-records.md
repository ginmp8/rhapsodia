# Execution Records

Load when execution updates tasks.md, spec-catalog.yaml, manifest.yaml, validation.md, or notes.md.

## Ownership Boundary

- Records live under `BOARD_ROOT`; `board_id` and `cycle_version` must be concrete before reads/writes.
- prd.md is input. tasks.md is read-mostly; only toggle an existing checkbox when that task truthfully reached done.
- Do not create, refine, split, resequence, rewrite, or correct task prose, ids, order, dependencies, or metadata.
- If honest execution requires task-plan or metadata changes, stop and hand off to planning.
- Use `assets/templates/tasks.md.template` only through `scripts/write_artifact_scaffold.py` when seeding, or as read-only contract reference after script validation.

## Planning-Origin Package Rules

- Treat planning fields as execution contract inputs; preserve fields/provenance while executing.
- Do not classify implementation requirement, roadmap/governance provenance, or pre-execution planned status as blockers.
- If an old log recorded that invalid blocker, do not repeat it as current truth; correct only when the task is re-executed or repaired with evidence.

## Canonical Structure

- spec-catalog.yaml: preserve `schema_version`, `board_id`, `cycle_version`, `board_status`, `specs`; per spec preserve `order`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `depends_on_features`, `depends_on_specs`, `status`, `feature_version`.
- manifest.yaml: preserve field set/order, including `schema_version`, identity fields, `status`, `phase`, `board_id`, `cycle_version`, `source_of_truth`, `traceability`, and optional last_execution. Canonical last_execution keeps `task_id` required and `date`, `summary`, `files_changed` optional.
- tasks.md: preserve phase headings, task order, task ids, metadata, and only toggle existing checkboxes for tasks completed in the current run.
- validation.md: preserve H1, `Validation Strategy`, `Validation Scope`, `Performance Validation`, and `Final Verification Checklist`.
- notes.md: preserve canonical top sections and Execution Log labels Status, Summary, Changes, Context Docs, Decisions, Follow-Ups, Blockers. Status values: not_started, in_progress, blocked, done; use none for intentionally empty fields.

## Writing Rules

Resource anchors: `assets/templates/` contains canonical templates; `scripts/write_execution_log.py` is the canonical execution-log writer.


- For notes.md or validation.md edits, load `references/markdown-writing.md`.
- Seed/refresh/normalize template-backed artifacts with `scripts/write_artifact_scaffold.py <artifact-path>` or a narrower script; do not copy templates manually.
- Populate supported template lists with `scripts/update_template_lists.py <artifact-path> --data <payload.yaml>`; inspect shapes with `scripts/update_template_lists.py --schema --artifact-name <artifact>` and extend the script first if needed.
- Preserve headings, frontmatter keys, field labels, checklist/execution-log order, and truthful neighboring content.
- For notes.md Execution Log, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...`; it keeps `## Execution Log` last, removes stale same-task copy, and appends the refreshed subsection.
- Never overwrite truthful dynamic values with placeholders or example literals.
- When completion state or records changed, use `scripts/close_execution_state.py` so sync, narrow self-healing, and validation happen together.
- Fall back to `scripts/sync_execution_state.py <board_root> --spec-id <specNNN> ...` plus `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` only when close wrapper is unavailable.
- Use `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` only for narrow mechanical reconciliation already proven by notes.md and validation.md; never invent validation, rewrite tasks, or repair task ids.
- Validate touched artifacts with `scripts/validate_artifact.py <artifact-path>` before closure.
- Run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` before closure when local repo files exist.
- Toggle tasks.md and validation.md checkboxes in place; keep attached context immediately below each item.
- Update manifest.yaml last_execution only when a real task executed; otherwise preserve truthful existing value or omit it.

## Cross-Artifact Consistency

- Any taskNNN in notes.md Execution Log or `manifest.yaml.last_execution.task_id` must exist in tasks.md.
- Tasks completed in the current run must have existing tasks.md boxes checked before closure.
- Tasks recorded as executed in notes.md should have matching validation.md evidence.
- Preserve truthful legacy last_execution unless current direct evidence is better.
- If manifest.yaml or spec-catalog.yaml is done, required tasks must not remain open in tasks.md.
- Do not duplicate execution evidence across noncanonical docs.
