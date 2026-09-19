# RALPH Mode

Use RALPH when execution is driven by the canonical registry-backed spec model under `BOARD_ROOT`.

## Canonical Rules

- `BOARD_ROOT` is required for the active board contract.
- Selected package path: `{BOARD_ROOT}/specs/<spec_id>/`.
- Prompt `BOARD_ROOT` takes precedence only after validation; derive selected package from canonical pattern.
- Keep durable MAGIA docs under `BOARD_ROOT`; keep spec-local execution records under the selected package.
- Specs, PRDs, tasks, technical designs, roadmaps, and governance records authored outside MAGIA are execution inputs, not implementation bans.

## Roots

Resolve concrete repo-relative `BOARD_ROOT` from references/canonical-paths.md. `board_id`, `year`, and `cycle_id` are required and never placeholders. Use explicit roots only when they match canonical board shape and repo truth. If both explicit roots and registry-selected spec exist, prefer the registry-selected spec. Ordering/status come from spec registry; local docs from `{BOARD_ROOT}/specs/<spec_id>/`. Treat notes.md and validation.md as Mago-owned planning inputs; write execution truth to implementation-notes.md and validation-evidence.md. Auxiliary docs/source refs under `BOARD_ROOT` are read-only unless selected task targets them. Do not create/update MAGIA planning, execution, validation, or architecture docs outside `BOARD_ROOT`.

## Planning-Origin Handoff

Load `references/planning-handoff.md` when the package came from planning, roadmap, discovery, governance, or migration workflows. Treat it as MAGIA's executable contract. `status: planned`, `phase: define`, roadmap/discovery/governance provenance, or implementation requirement is starting state, not a blocker. Block only for concrete missing execution evidence, contradictions, unsafe paths, unavailable dependencies, or required planning changes.

## Workflow

1. Resolve `BOARD_ROOT` and selected package path.
2. Load board spec registry; selected manifest, PRD, tasks, validation.md as validation plan, notes.md as planning context, implementation-notes.md and validation-evidence.md when present; technical design when present and needed; only relevant auxiliary docs/source refs/tests/repo files.
3. Treat prd.md as read-only and tasks.md as read-mostly; only toggle an existing checkbox when truthfully complete.
4. Use tasks.md for order/scope/dependencies/metadata/checkbox state; implementation-notes.md Execution Log for detailed history; manifest.yaml last_execution for most recent truthful executed task.
5. Execute one task by default, or a dependency-safe batch when `TASK_BATCH_SIZE` requires.
6. Implement code, config, tests, scripts, migrations, tooling, or docs when the task requires them and repo evidence bounds execution.
7. Update records truthfully: use `scripts/write_execution_log.py <board_root> --spec-id <spec_id> --task-id <taskNNN> ...`; check only existing tasks.md boxes for tasks completed in this run; leave unchecked for not_started, in_progress, or blocked.
8. Record real evidence in validation-evidence.md, including commands, skipped checks with reasons, residual gaps, and blockers. Keep validation.md as the read-only validation plan.
9. Sync manifest.yaml and the matching registry entry: use `manifest.yaml phase: execute` during active implementation; `manifest.yaml phase: done` only when the selected spec is fully complete and validated; update last_execution only for a task truthfully executed or already truthfully recorded, keeping `task_id` required and `date`, `summary`, `files_changed` only with current evidence.
10. When task completion or records changed, use `scripts/close_execution_state.py <board_root> --spec-id <spec_id> --task-id <taskNNN> --status <in_progress|blocked|done> ...`; the sync step validates a candidate snapshot and commits through a recoverable transaction. Run `scripts/heal_execution_state.py` separately before closure only for previously evidenced narrow drift. Fall back to `scripts/sync_execution_state.py <board_root> --spec-id <spec_id> ...` plus `scripts/validate_execution_state.py <board_root> --spec-id <spec_id>` only when wrapper is unavailable.
11. Run `scripts/validate_repo_board.py <repo_root> --board-root <board_root>` before final response when local repo files exist.

## Task Selection

Run `scripts/validate_execution_readiness.py <board_root> --spec-id <spec_id> --task-id <taskNNN>` before mutation. The selected task must resolve to a current PRD objective or acceptance criterion and to a planned validation check. Prefer shared `OBJ-###`/`GOAL-###`/`REQ-###`, `AC-###`, and `VAL-###` anchors; legacy packages may use deterministic shared domain terms. Reject merely co-located but unrelated task, intent, and validation text.

Prefer the next actionable unchecked task with satisfied dependencies and no done log. Respect dependencies and listed task order; do not select a later open task while an earlier required task remains open. A task may bypass list order only when planning already marks it `[parallel]` or `[independent]`. Do not add or rewrite those markers. Do not skip a blocked dependency unless asked for audit/repair. Prefer tasks that unblock others. Do not broaden weak tasks. Treat `task001`-style ids as stable selectors. No Execution Log subsection means not executed. Update existing log subsections instead of scattering facts. Honor metadata/specialist fields as input only; do not add, rewrite, or correct them. If implementation-notes.md or manifest.yaml last_execution references missing taskNNN, or required metadata is missing/malformed, stop and hand off to planning. If legacy execution content exists only in notes.md or validation.md, run ADAPT mode before RALPH execution or treat it as unavailable. If drift is only unchecked done task or stale/missing last_execution and implementation-notes.md plus validation-evidence.md prove repair, run `scripts/heal_execution_state.py <board_root> --spec-id <spec_id>` before blocking. Before execution, confirm alignment with prd.md, current repo state, dependencies, and bounded scope; otherwise block and hand off. Do not treat implementation requirement, planning provenance, roadmap provenance, or `phase: define` as blocker.

## Blockers

Return BLOCKED only for concrete execution blockers: missing targets, unresolved dependencies, unavailable credentials, contradictory source-of-truth, missing validation path, unsafe secret access, or required changes to product intent/task definitions. Do not record blockers such as task requires implementation or package was authored by planning.

## Batch Execution

When `TASK_BATCH_SIZE > 1`, select up to that many next unfinished dependency-safe tasks; execute sequentially; run each task's bounded validation before continuing when supported; stop early on a clear blocker. For partial batches, sync completed tasks as done, record blocked task as blocked with unchecked box in implementation-notes.md, and point manifest.yaml last_execution to the most recent truthfully executed task. Do not exceed the selected batch.

## Unattended Loop Protocol

Do not ask for next actions when a selected task exists. Do not run recursive agent, Copilot, MAGIA, MAGO, or RALPH loops from inside selected execution. Do not use a missing `task_complete` tool as a reason to keep generating prose, create substitute tags, or invent completion markers. End with concise evidence and exact status token when the caller requires it. Let the orchestrator handle commit, push, retry, timeout, and task selection when prompt assigns those responsibilities.
