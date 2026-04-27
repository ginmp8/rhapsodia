# Common Execution

## Operational Roots

- load canonical defaults from references/canonical-paths.md
- `BOARD_ROOT` is the active board root for the run
- use prompt-provided `BOARD_ROOT` when present; otherwise derive it from the canonical defaults with concrete `board_id` and `cycle_version`
- for spec-scoped execution, derive the selected spec package path from `BOARD_ROOT` with concrete `spec_id`
- every execution record path, validator target, and durable docs location must resolve from `BOARD_ROOT`

## Source of Truth

- repository code, runtime evidence, and the active docs contract
- in RALPH: the board spec catalog plus the selected package files under `{BOARD_ROOT}/specs/<spec_id>/`
- `board_id` and `cycle_version` are mandatory concrete dynamic path segments for every RALPH run
- auxiliary docs may exist under the active `BOARD_ROOT`; treat them as read-only evidence unless the selected task explicitly requires updating them
- do not invent product rules, scope, or status claims that belong in those files

## Core Rules

- prefer the smallest safe implementation that satisfies the selected work
- read the relevant code and docs before editing
- validation is mandatory; code change alone is not completion
- when work is underdefined, derive the smallest concrete implementation only if the selected task already bounds the work enough for honest execution
- translate the selected task into at least one concrete success check before editing
- prefer the simplest implementation a senior engineer would consider sufficient
- preserve truthful supported behavior unless the active contract explicitly allows change
- touch only the files and abstractions needed for that implementation
- if the active package carries original-solution or source-reference paths, use them only as read-only evidence for behavior and traceability
- in RALPH, treat prd.md as read-only and tasks.md as read-mostly; execution may only toggle an existing task checkbox in place when that task is truthfully complete
- when editing execution records, load `references/artifacts/execution-records.md` and preserve canonical structure in place
- use local scripts for every available template operation: `scripts/write_artifact_scaffold.py` for template-backed writes and `scripts/validate_artifact.py` or the narrower validator script for validation; never let template copying, placeholder resolution, or structure validation depend only on LLM judgment when a script exists
- keep all MAGIA-created or MAGIA-updated durable documentation inside `BOARD_ROOT`
- record meaningful assumptions or trade-offs in notes.md when they affect later work
- after each executed task, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...` to append or refresh that task's Execution Log subsection at EOF; if the task is truthfully done, check its existing checkbox in tasks.md in place
- when execution evidence changes completion truth, keep summary and proof synchronized in one closure pass:
  - check an existing tasks.md checkbox only when that task truthfully reached done
  - check an existing validation.md final checklist item only when current evidence truthfully satisfies it
  - reconcile tasks.md, notes.md, validation.md, manifest.yaml, and spec-catalog.yaml together so completion, evidence, and status cannot drift apart
- if tasks.md, notes.md, or manifest.yaml disagree about valid taskNNN ids, stop and hand off to planning instead of repairing execution inputs
- if execution-state drift is limited to unchecked done tasks or stale or missing manifest.yaml last_execution, and the repair is mechanically derivable from existing notes.md plus validation.md evidence, run `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` before treating the package as blocked
- do not ask for clarification during unattended loops
- continue conservatively only when the result remains honest and verifiable
- if ambiguity would require inventing tasks, correcting task metadata, rewriting the PRD, resequencing the plan, or otherwise planning work inside execution, stop and hand off to the planning workflow instead of improvising

## Context Loading

- always load the files directly referenced by the user or prompt, the files directly impacted by the change, and the active docs contract in RALPH mode
- load additional context only when clearly needed: nearby tests, public APIs, sensitive architecture, or hot-path performance context
- avoid broad context expansion "just in case"

## Editing Rules

- Reuse existing abstractions before adding new ones.
- Avoid unrelated refactors.
- Keep comments and docs aligned with behavior changes.
- Preserve local naming and style unless the task requires change.
- Update execution records in place.
- Do not rewrite large areas when a focused edit is enough.
- Do not create duplicate notes, validation, or execution summaries outside `BOARD_ROOT`.

## Compatibility

Default stance: preserve compatibility.

Do not preserve fake, placeholder, misleading, or overstated behavior merely for continuity. If the active contract says current behavior is deceptive or blocks truthful delivery, replacement or removal is preferred.
