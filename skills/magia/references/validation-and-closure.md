# Validation and Closure

## Validation Policy

Run the smallest validation set that proves the selected work is correct.

- typical validation: targeted unit or integration tests, build or compile checks, schema or parser checks, and lint or formatting only when changed files participate in those checks or repository policy requires them
- when behavior changes and coverage tooling exists for the changed area, run targeted coverage if it can be done with the existing test harness; otherwise record the uncovered gap in validation.md

## Execution Records Sync

Keep execution records truthful:

- preserve stable task ids when recording execution history
- keep blockers explicit and tied to concrete execution facts
- record factual decisions, assumptions, and trade-offs in notes.md
- keep durable MAGIA documentation inside `BOARD_ROOT`
- after each executed task, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...` to append or refresh that task's Execution Log subsection in notes.md when the local script is available
- each executed task subsection must record at least: Status, Summary, Changes, Context Docs, Decisions, Follow-Ups, and Blockers
- use Context Docs to list repository-relative POSIX paths to docs created or updated under `BOARD_ROOT`, or none
- use none when an execution-log field is intentionally empty
- use Follow-Ups to capture architecture, behavior, migration, or dependency implications that later tasks need
- if a task truthfully executed in this run, update manifest.yaml last_execution to that taskNNN; keep `task_id` required and add `date`, `summary`, or `files_changed` only when they are truthful for this run; if no task executed, do not invent last_execution
- record real commands, evidence, outcomes, and residual gaps in validation.md
- when execution records are touched, follow `references/artifacts/execution-records.md`
- when a touched execution record is template-backed, validate it with `scripts/validate_artifact.py <artifact-path>` or the narrower local validator before relying on manual review
- apply the common execution sync invariant before closing so tasks.md, validation.md, notes.md, manifest.yaml, and spec-catalog.yaml stay aligned
- when task completion state changed truthfully in this run or execution records changed and the local script is available, use `scripts/close_execution_state.py` before the final manual closure review
- fall back to `scripts/sync_execution_state.py <board_root> --spec-id <specNNN> ...` plus `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` only when `scripts/close_execution_state.py` is unavailable
- when the package is blocked only by narrow execution-state drift already evidenced by notes.md and validation.md, run `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` before handing off to planning
- run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` before final response when local repository files are available
- when a validation.md final checklist item becomes true because the work and evidence are complete, check that box in place during the same closure pass; if it remains unchecked, record the real gap or blocker and do not claim full completion
- move both manifest.yaml and spec-catalog.yaml to in_progress only when implementation really started
- set `manifest.yaml phase: execute` when implementation really started
- mark both manifest.yaml and spec-catalog.yaml done only when required work, required checklist items, and validation are complete
- set `manifest.yaml phase: done` only when required work, required checklist items, and validation are complete
- if any required task is not recorded as done in notes.md, any required final checklist item remains unchecked, or validation evidence is still missing, do not mark the spec done
- if notes.md or manifest.yaml last_execution references a taskNNN missing from tasks.md, stop closure and hand off to planning instead of repairing the package during execution

## Underdefined Task Handling

1. derive the narrowest concrete objective that still satisfies the selected task and active spec package
2. define at least one observable validation check before treating the work as complete
3. implement only the code, docs, and tests needed for that bounded objective
4. record assumptions and residual ambiguity in notes.md when they materially affect future work
5. if execution creates new durable docs or architecture guidance, place them under `BOARD_ROOT` and list them in that task's Context Docs field in notes.md

If no honest and verifiable objective can be derived without changing the task plan, stop and treat the task as blocked and hand off to the planning workflow. Do not use implementation requirement or planning provenance alone as the blocker.

## Blockers

1. stop broadening scope
2. classify the blocker as a concrete execution blocker, not an authoring-boundary assumption
3. record the blocker clearly in notes.md and validation.md
4. preserve partial truth in docs
5. do not mark the task done

Valid blockers include missing implementation targets, unresolved dependencies, unavailable credentials or services, contradictory source-of-truth artifacts, unsafe secret access, missing validation path, or required planning changes. Invalid blockers include implementation being required, the package being authored by a planning workflow, roadmap provenance, governance provenance, or pre-execution manifest state such as `status: planned`.

Report what is blocked, why, what was completed, what concrete evidence is missing, and what remains.

## Final Closure Pass

1. verify the changed code matches the selected work
2. verify spec-catalog.yaml and manifest.yaml match actual execution state, and if either changed in this run they were reconciled together
3. verify manifest.yaml uses phase: execute for active work and phase: done only for fully completed work
4. verify the selected task's tasks.md checkbox and notes.md Execution Log subsection match actual completion state
5. verify manifest.yaml last_execution is omitted or points to an existing truthful taskNNN
6. verify validation.md records real evidence and that satisfied required checklist items are checked
7. verify notes.md reflects blocker and decision truth
8. verify every executed task has a truthful Execution Log subsection and no execution-log subsection references a missing task
9. verify no required canonical section, field, or checklist structure disappeared from touched execution records
10. verify no MAGIA-created or MAGIA-updated durable documentation exists outside `BOARD_ROOT`
11. run `scripts/close_execution_state.py ...` when task completion or execution records changed; otherwise run `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` when available and, for narrow mechanical drift only, try `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` before closing the run as blocked
12. run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` when local repository files are available

## Final Response

Summarize what changed, what validation ran, what passed or failed, assumptions or trade-offs, blockers, and what remains next.
