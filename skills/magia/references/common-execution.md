# Common Execution

## Operational Roots

- Load references/canonical-paths.md first.
- `BOARD_ROOT` is the active root; use prompt-provided `BOARD_ROOT` after validation or derive it from concrete `board_id`, `year`, and `cycle_id`.
- For spec work, derive `{BOARD_ROOT}/specs/<spec_id>` with concrete `spec_id`.
- Resolve execution records, validators, and durable docs from `BOARD_ROOT`.

## Source of Truth

- Use repository code, runtime evidence, tests, command output, and the active docs contract.
- In RALPH, use the board selected registry entry plus selected files under `{BOARD_ROOT}/specs/<spec_id>`; provenance is not an implementation ban.
- `board_id`, `year`, and `cycle_id` are mandatory concrete path segments for RALPH.
- Treat auxiliary docs under `BOARD_ROOT` as read-only unless the selected task requires updating them.
- Do not invent product rules, scope, or status.

## Planning-Origin Execution Inputs

- Planning authorship means the artifact was not implemented by its authoring workflow; specs/docs from planning or governance are executable inputs for MAGIA.
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
- In RALPH, prd.md, technical-design.md, notes.md, and validation.md are read-only planning inputs; tasks.md is read-mostly and may only have an existing task checkbox toggled when truthfully complete.
- For execution records, load `references/artifacts/execution-records.md` and preserve canonical structure.
- Use local scripts for template writes, dynamic-token resolution, execution logs, state sync/heal, artifact validation, and boundary/package validation when available.
- Use `scripts/write_artifact_scaffold.py --board-root <board_root> <artifact-path>` for RALPH template-backed writes; use explicit `--allowed-root <root>` for authorized ADHOC documentation writes and `scripts/validate_artifact.py` or a narrower validator before relying on manual review.
- Keep MAGIA durable docs inside `BOARD_ROOT`.
- Record meaningful execution assumptions/trade-offs in implementation-notes.md when they affect later work; keep notes.md as read-only planning context.
- After each executed task, use `scripts/write_execution_log.py <board_root> --spec-id <spec_id> --task-id <taskNNN> ...` to update implementation-notes.md; if truthfully done, check the existing tasks.md box in place.
- When evidence changes completion truth, reconcile tasks.md, implementation-notes.md, validation-evidence.md, manifest.yaml, and the matching registry entry in one closure pass.
- If tasks.md, implementation-notes.md, or manifest.yaml disagree about valid taskNNN ids, stop and hand off to planning.
- For narrow drift limited to unchecked done tasks or stale/missing manifest.yaml last_execution, run `scripts/heal_execution_state.py <board_root> --spec-id <spec_id>` only when implementation-notes.md plus validation-evidence.md prove the repair. Legacy notes.md/validation.md are not fallback evidence; run ADAPT mode first if they are the only source.
- Do not ask for clarification during unattended loops; continue conservatively only when honest and verifiable.
- Stop instead of improvising when ambiguity would require inventing tasks, correcting metadata, rewriting PRD, resequencing, or doing planning inside execution.

## Context Loading

- Always load files directly referenced by the user, impacted files, and the active docs contract in RALPH.
- Add context only when needed: nearby tests, public APIs, sensitive architecture, or hot paths.
- Avoid broad context expansion just in case.

## Editing Rules

- Avoid unrelated refactors and duplicate planning notes, validation plans, or execution summaries outside `BOARD_ROOT`.
- Keep comments/docs aligned with behavior changes.
- Preserve local naming/style unless the task requires change.
- Update execution records in place; do not rewrite large areas when a focused edit works.

## Compatibility

Default: preserve compatibility. Do not preserve fake, unresolved-token, misleading, or overstated behavior merely for continuity; replace or remove it when the active contract says it blocks truthful delivery.
