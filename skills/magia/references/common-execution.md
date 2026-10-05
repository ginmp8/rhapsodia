# Common Execution

Default storage is `artifact-native`. Use this reference for execution rules shared by ADHOC, RALPH, and ADAPT. Board/registry/cycle mechanics apply only when `legacy-board` was explicitly selected; they never override native ownership, evidence, privacy, or validation rules.

## Operational Roots

- Resolve the repository root and authorized write scope first.
- Native Magia evidence defaults to `docs/implementation/<work_item_id>/` or another explicitly authorized non-overlapping Magia owner root; see `references/artifact-native.md`.
- RALPH native planning inputs stay in their Mago planning directory and are read-only to Magia; Magia writes only owner-local execution state/evidence plus authorized repository changes.
- `BOARD_ROOT`, cycle, registry, and spec-package paths are required only in explicit `legacy-board` compatibility; validate them through `references/canonical-paths.md` and `references/board-contract.md` before use.

## Source of Truth

- Use current repository code/config/docs, runtime evidence, tests, command output, and validated active contracts.
- In native RALPH, use the validated `mago_to_magia` handoff plus its source-bound planning/task/validation references; planning provenance is not an implementation ban.
- In legacy-board RALPH, use the validated selected registry/spec package under `BOARD_ROOT`.
- Treat foreign-owner planning/governance artifacts as read-only inputs unless a handoff changes ownership explicitly.
- Do not invent product rules, scope, completion state, or evidence.

## Planning-Origin Execution Inputs

- Planning authorship means the artifact was not implemented by its authoring workflow; specs/docs from planning or governance are executable inputs for MAGIA.
- Implement the smallest safe repo change when the selected task requires implementation and no concrete blocker remains.
- Never block solely because implementation is required, the package was planned, or a planning state is not yet execution-complete.
- A valid blocker names missing/contradictory target evidence, dependency, credential/service, validation path, unsafe access, or a required planning/governance decision.

## Core Rules

- Prefer the smallest safe implementation that satisfies selected work.
- Read relevant code/docs before editing and define at least one observable success check before completion.
- When work is underdefined, derive only the narrowest implementation bounded by current intent plus repository evidence.
- Preserve supported behavior unless the active contract explicitly permits change.
- Touch only files/abstractions needed; reuse existing patterns before adding new ones.
- Keep all Mago/Nomia canonical artifacts read-only in native mode. Write Magia execution records/evidence only under the resolved Magia artifact root.
- In native RALPH, bind evidence to the selected planning/task identity and current candidate bytes; use `scripts/native_execution.py` and `scripts/native_artifacts.py` as applicable.
- In legacy-board only, `prd.md`, `technical-design.md`, `notes.md`, and `validation.md` remain planning inputs; `tasks.md` is read-mostly and an existing checkbox may be toggled only when truthfully complete. Use Board state scripts only in that profile.
- Load `references/artifacts/execution-records.md` before controlled execution-state writes and preserve its ownership rules.
- Load only the branch-specific contracts needed for the current decision; do not require multi-hop Markdown discovery for mandatory execution rules.
- Record material assumptions/trade-offs in Magia-owned implementation evidence when they affect later work.
- Never use legacy `notes.md`/`validation.md` execution claims as fallback proof; run ADAPT first when they are the only source.
- Do not ask for clarification during explicitly unattended loops when a safe bounded action is already derivable; otherwise stop rather than invent tasks, metadata, acceptance, sequencing, or architecture.

## Context Loading

- Always load directly supplied files, impacted files, and the active execution contract.
- Add nearby tests, public APIs, sensitive architecture, hot paths, or extra planning evidence only when the active change makes them material.
- Avoid broad context expansion "just in case"; prefer direct one-level references from `SKILL.md`.

## Editing Rules

- Avoid unrelated refactors and duplicate planning/governance records.
- Keep comments/docs aligned with behavior changes and local conventions unless unsafe.
- Keep durable Magia evidence inside the resolved Magia owner root; legacy-board outputs remain inside validated `BOARD_ROOT` only in that explicit profile.
- Update execution records narrowly and transactionally; do not rewrite large areas when a focused edit works.

## Compatibility

Default: preserve compatibility. Do not preserve fake, unresolved-token, misleading, unsafe, or overstated behavior merely for continuity; change or remove it only when the active contract and authority permit that change and current validation supports it.
