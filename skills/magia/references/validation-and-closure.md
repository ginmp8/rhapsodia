# Validation and Closure

## Validation Policy

Run the smallest validation set that proves selected work: targeted unit/integration tests, build/compile, schema/parser checks, lint/format only when changed files participate or policy requires. If behavior changed and coverage tooling exists, run targeted coverage when available; otherwise record the gap in validation.md.

## Execution Records Sync

Keep records truthful:

- preserve stable task ids; tie blockers to concrete execution facts;
- record factual decisions, assumptions, and trade-offs in notes.md;
- keep durable MAGIA docs under `BOARD_ROOT`;
- after each executed task, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...` when available;
- each executed task subsection records Status, Summary, Changes, Context Docs, Decisions, Follow-Ups, Blockers; use none for intentionally empty fields;
- Context Docs lists repository-relative POSIX paths under `BOARD_ROOT`, or none;
- use Follow-Ups for architecture, behavior, migration, or dependency implications;
- if a task executed, update manifest.yaml last_execution to that taskNNN; keep `task_id` required and add `date`, `summary`, `files_changed` only when true for this run; invent no last_execution;
- record real commands, outcomes, residual gaps, and skipped checks in validation.md;
- when records are touched, follow `references/artifacts/execution-records.md` and validate template-backed artifacts with `scripts/validate_artifact.py <artifact-path>` or narrower validator;
- reconcile tasks.md, validation.md, notes.md, manifest.yaml, and spec-catalog.yaml before close;
- when completion state or records changed, use `scripts/close_execution_state.py`; fall back to `scripts/sync_execution_state.py <board_root> --spec-id <specNNN> ...` plus `scripts/validate_execution_state.py <board_root> --spec-id <specNNN>` only if close wrapper is unavailable;
- for narrow drift already evidenced by notes.md and validation.md, run `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` before planning handoff;
- run `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` before final response when local repo files exist;
- check validation.md final checklist items only when work/evidence satisfies them; otherwise record gap/blocker;
- move manifest.yaml and spec-catalog.yaml to in_progress only when implementation started;
- set `manifest.yaml phase: execute` only for active implementation and `manifest.yaml phase: done` only when required work, required checklist items, and validation are complete;
- do not mark done if any required task is not done in notes.md, checklist item remains unchecked, or validation evidence is missing;
- if notes.md or manifest.yaml last_execution references a taskNNN missing from tasks.md, stop closure and hand off to planning.

## Underdefined Tasks

1. Derive the narrowest concrete objective satisfying the selected task and active spec.
2. Define at least one observable validation check before completion.
3. Implement only needed code/docs/tests.
4. Record material assumptions and ambiguity in notes.md.
5. Put new durable docs/guidance under `BOARD_ROOT` and list them in Context Docs.

If no honest verifiable objective can be derived without changing the task plan, stop as blocked and hand off. Implementation requirement, planning provenance, roadmap provenance, governance provenance, or pre-execution `status: planned` are not blockers.

## Blockers

Stop broadening scope; classify a concrete execution blocker; record it in notes.md and validation.md; preserve partial truth; do not mark task done. Valid blockers: missing targets, unresolved dependencies, unavailable credentials/services, contradictory source-of-truth, unsafe secret access, missing validation path, or required planning changes. Report what is blocked, why, what completed, missing evidence, and what remains.

## Final Closure Pass

Verify: changed code matches selected work; spec-catalog.yaml and manifest.yaml match actual state and were reconciled together if changed; manifest phase is execute for active work or done only for full completion; tasks.md checkbox and notes.md Execution Log match completion; last_execution is omitted or points to an existing truthful taskNNN; validation.md records real evidence and checked items are satisfied; notes.md reflects blockers/decisions; every executed task has a truthful log and no log references a missing task; canonical sections/fields/checklists survived; no MAGIA durable docs exist outside `BOARD_ROOT`. Run `scripts/close_execution_state.py ...` when state changed; otherwise run validation/state scripts as applicable, including `scripts/validate_repo_board.py <repo_root> --board_id <board_id> --cycle_version <cycle_version>` when local files exist.

## Final Response

Summarize changed, validated, passed/failed/not-run checks, assumptions/trade-offs, blockers, residual risk, and next remaining work.
