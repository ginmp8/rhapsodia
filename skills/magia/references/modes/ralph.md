# RALPH Mode

## Canonical Rules

- `BOARD_ROOT` is required for the active board contract.
- The selected spec package path is always `{BOARD_ROOT}/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected spec package path from the canonical pattern.
- Keep durable MAGIA docs under `BOARD_ROOT` and spec-local execution records under the selected package path.

Use RALPH when execution is driven by the sequential spec model under `BOARD_ROOT`.

## Roots

- resolve the concrete repository-relative `BOARD_ROOT` and derive the selected package path from [../canonical-paths.md](../canonical-paths.md)
- `board_id` and `cycle_version` are required concrete dynamic path segments; never leave them as placeholders.
- if the prompt supplies explicit roots, use them only when they match the canonical board shape and repository truth
- if both explicit roots and a catalog-selected spec exist, prefer the catalog-selected spec
- ordering and high-level status come from `{BOARD_ROOT}/spec-catalog.yaml`; local execution docs come from `{BOARD_ROOT}/specs/<spec_id>/`
- auxiliary docs or source-reference files may also exist under `BOARD_ROOT`; load them only when needed and treat them as read-only unless the selected task truthfully targets them
- do not create or update MAGIA planning, execution, validation, or architecture documentation outside `BOARD_ROOT`

## Ralph Workflow

1. Resolve `BOARD_ROOT` and derive the selected package path.
2. Load:
   - `{BOARD_ROOT}/spec-catalog.yaml`
   - `{BOARD_ROOT}/specs/<spec_id>/manifest.yaml`
   - `{BOARD_ROOT}/specs/<spec_id>/prd.md`
   - `{BOARD_ROOT}/specs/<spec_id>/tasks.md`
   - `{BOARD_ROOT}/specs/<spec_id>/validation.md`
   - `{BOARD_ROOT}/specs/<spec_id>/notes.md`
   - only the directly relevant auxiliary docs or source-reference files needed for the selected task
3. Treat `prd.md` as read-only. Treat `tasks.md` as read-mostly: execution may only toggle an existing checkbox in place when that task is truthfully complete.
4. Use `tasks.md` for task order, scope, and completion-checkbox state, and use `notes.md` `Execution Log` as the authoritative detailed execution history; when `manifest.yaml.last_execution` exists, keep it aligned with the most recent truthful executed task.
5. Execute one task by default, or a dependency-safe batch when `TASK_BATCH_SIZE` requires it.
6. Update execution records truthfully as progress changes.
   - maintain `notes.md` `Execution Log` entries per executed `taskNNN` using `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...` when the local script is available
   - check only the existing `tasks.md` checkbox for a task truthfully completed in this run
   - leave the checkbox unchecked for `not_started`, `in_progress`, or `blocked` work
7. Record real evidence in `validation.md`.
8. Synchronize `manifest.yaml` and `spec-catalog.yaml` before finishing:
   - use `manifest.yaml phase: execute` during active implementation
   - use `manifest.yaml phase: done` only when the selected spec is fully complete and validated
   - update `manifest.yaml.last_execution` only for a task that truthfully executed in this run or was already truthfully recorded
   - when writing `manifest.yaml.last_execution`, keep `task_id` required and use `date`, `summary`, and `files_changed` only when current run truth supports them
9. When task completion state or execution records changed and the local script is available, use `scripts/close_execution_state.py <board_root> --spec-id <specNNN> --task-id <taskNNN> --status <in_progress|blocked|done> ...` before final closure. The closure path may self-heal narrow execution-state drift that is mechanically derivable from existing evidence. Fall back to `scripts/sync_execution_state.py <board_root> --spec-id <specNNN> ...` followed by `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` only when the wrapper is unavailable.
10. Run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` before final response when local repository files are available.

## Task Selection

- Prefer the next actionable task whose dependencies are satisfied, whose checkbox is still unchecked, and that is not already recorded as `done` in `notes.md` `Execution Log`.
- Respect dependencies.
- Prefer tasks that unblock other tasks.
- Do not broaden scope to compensate for a weak task definition.
- Treat task ids such as `task001` as the stable selectors inside the current spec.
- If a task has no `Execution Log` subsection yet, treat it as not yet executed.
- Treat `notes.md` `Execution Log` task subsections as durable execution memory for later runs; update them instead of scattering execution facts across unrelated sections.
- Honor task metadata, including specialist fields, as input only; do not add, rewrite, or correct it during execution.
- If `notes.md` or `manifest.yaml.last_execution` references a `taskNNN` missing from `tasks.md`, stop and hand off to the planning workflow.
- If required task metadata is missing or malformed, stop and hand off to the planning workflow.
- If package drift is only an unchecked done task or stale or missing `manifest.yaml.last_execution`, and `notes.md` plus `validation.md` already contain enough evidence to repair it mechanically, run `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` before blocking the run.
- Before execution, confirm the task is aligned with `prd.md`, actionable from current repo state, dependency-safe, and not so broad that it requires unbounded interpretation.
- If this check fails, treat the task as blocked and hand off to the planning workflow rather than repairing the task inside execution.

## Batch Execution

- When `TASK_BATCH_SIZE > 1`, select up to that many next unfinished and dependency-safe tasks, execute sequentially, run each task's bounded validation before continuing when the repository already supports it, and stop early on a clear blocker.
- For a partial batch, keep already-completed tasks synchronized as `done` with checked checkboxes, record the blocked task as `blocked` with an unchecked checkbox, and point `manifest.yaml.last_execution` to the most recent task that truthfully executed.
- Do not execute beyond the selected batch.
