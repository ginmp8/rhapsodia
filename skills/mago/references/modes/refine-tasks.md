# Refine Tasks Mode

## Canonical Rules

- Resolve one canonical registry-backed package.
- Read and modify `tasks.md` only.
- Preserve stable IDs, truthful completion checkboxes, and task IDs referenced by MAGIA evidence.

## Task Refinement Workflow

1. Read current `tasks.md` and preserve what is still true.
2. Load only adjacent planning/repository evidence needed to keep tasks aligned.
3. Tighten task wording, affected boundaries, dependencies, phase placement, reasoning, specialist metadata, validation, and expected results.
4. Normalize mechanically when useful, then run artifact/package validation.
5. Stop once the task plan is clearer and remains inside current product intent.

## Boundaries

- do not alter PRD, notes, validation, manifest, registry identity/dependencies/handoff, generated views, or execution evidence;
- do not infer progress, completion, blocker state, or rollout state;
- do not widen product scope or backfill missing rationale;
- when contradictions cannot be resolved from tasks alone, switch to full `refine` or the relevant product mode.

## Refinement Focus

Preserve canonical phase order, current initiative boundary, completed history, and visible cross-artifact task references. Keep changes minimal when the task plan is already coherent. Do not renumber or fabricate history to hide drift.
