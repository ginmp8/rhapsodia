# Common Execution

## Operational Roots

- Load references/canonical-paths.md first.
- `BOARD_ROOT` is the active root; use prompt-provided `BOARD_ROOT` after validation or derive it from concrete `board_id` and `cycle_version`.
- For spec work, derive `{BOARD_ROOT}/specs/<spec_id>` with concrete `spec_id`.
- Resolve execution records, validators, and durable docs from `BOARD_ROOT`.

## Source of Truth

- Use repository code, runtime evidence, tests, command output, and the active docs contract.
- In RALPH, use the board spec catalog plus selected files under `{BOARD_ROOT}/specs/<spec_id>`; provenance is not an implementation ban.
- `board_id` and `cycle_version` are mandatory concrete path segments for RALPH.
- Treat auxiliary docs under `BOARD_ROOT` as read-only unless the selected task requires updating them.
- Do not invent product rules, scope, or status.

## Planning-Origin Inputs

- Specs/docs from planning or governance are executable inputs for MAGIA.
- Implement the smallest safe repo change when the selected task requires implementation and no concrete blocker remains.
- Never block solely because implementation is required, the package was planned, or the manifest is planned.
- A valid blocker names the missing target, dependency, credential, validation path, unsafe access, or conflicting source-of-truth evidence.

## Core Rules

- Prefer the smallest safe implementation that satisfies selected work.
- Read relevant code/docs before editing; define at least one concrete success check before completion.
- When work is underdefined, derive the narrowest implementation only if task plus repo evidence bound it honestly.
- Preserve truthful supported behavior unless the active contract permits change.
- Touch only files and abstractions needed; reuse existing abstractions first.
- Treat original-solution, planning, governance, roadmap, discovery, and source-reference paths as read-only evidence, not runtime bans.
- In RALPH, prd.md is read-only; tasks.md is read-mostly and may only have an existing task checkbox toggled when truthfully complete.
- For execution records, load `references/artifacts/execution-records.md` and preserve canonical structure.
- Use local scripts for template writes, placeholder resolution, execution logs, state sync/heal, artifact validation, and boundary/package validation when available.
- Use `scripts/write_artifact_scaffold.py` for template-backed writes and `scripts/validate_artifact.py` or a narrower validator before relying on manual review.
- Keep MAGIA durable docs inside `BOARD_ROOT`.
- Record meaningful assumptions/trade-offs in notes.md when they affect later work.
- After each executed task, use `scripts/write_execution_log.py <board_root> --spec-id <specNNN> --task-id <taskNNN> ...`; if truthfully done, check the existing tasks.md box in place.
- When evidence changes completion truth, reconcile tasks.md, notes.md, validation.md, manifest.yaml, and spec-catalog.yaml in one closure pass.
- If tasks.md, notes.md, or manifest.yaml disagree about valid taskNNN ids, stop and hand off to planning.
- For narrow drift limited to unchecked done tasks or stale/missing manifest.yaml last_execution, run `scripts/heal_execution_state.py <board_root> --spec-id <specNNN>` when notes.md plus validation.md prove the repair.
- Do not ask for clarification during unattended loops; continue conservatively only when honest and verifiable.
- Stop instead of improvising when ambiguity would require inventing tasks, correcting metadata, rewriting PRD, resequencing, or doing planning inside execution.

## Context Loading

- Always load files directly referenced by the user, impacted files, and the active docs contract in RALPH.
- Add context only when needed: nearby tests, public APIs, sensitive architecture, or hot paths.
- Avoid broad context expansion just in case.

## Editing Rules

- Avoid unrelated refactors and duplicate notes, validation, or execution summaries outside `BOARD_ROOT`.
- Keep comments/docs aligned with behavior changes.
- Preserve local naming/style unless the task requires change.
- Update execution records in place; do not rewrite large areas when a focused edit works.

## Compatibility

Default: preserve compatibility. Do not preserve fake, placeholder, misleading, or overstated behavior merely for continuity; replace or remove it when the active contract says it blocks truthful delivery.
