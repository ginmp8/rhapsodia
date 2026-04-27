# Define Tasks Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- The selected tasks-only package slice is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected package slice.
- Keep task-only authoring inside `BOARD_ROOT/specs/<spec_id>/`.

## Task Definition Workflow

1. Load only the directly relevant task inputs: the active product scope, discovery evidence, existing package docs, and repository facts needed to define executable work truthfully.
2. Create or reconcile tasks.md only.
3. Open `references/artifacts/templates-and-status.md` for the canonical tasks.md contract. Open references/specialist-spellbook.md for task specialist metadata, references/markdown-writing.md for Markdown edits, and use `scripts/write_artifact_scaffold.py` plus `scripts/validate_artifact.py` when tasks.md is template-backed.
4. Stop once tasks.md is concrete, dependency-safe, and aligned with the current product scope without widening into product or execution updates.

## Boundaries

- do not create or alter prd.md, notes.md, validation.md, manifest.yaml, or spec-catalog.yaml
- do not infer execution progress, completion, blockers, rollout state, or execution history
- do not redefine product scope, rewrite product decisions, or switch into product-only refinement
- if visible contradictions between tasks.md and adjacent docs cannot be resolved truthfully from tasks.md alone, stop or switch to `define`, `refine`, `define-product`, or `refine-product`
- if current docs lack enough product scope to define tasks truthfully, stop or switch to `define`, `refine`, `define-product`, or `refine-product`

## Task Focus

- create the smallest truthful tasks.md that fits the existing product scope
- follow the canonical tasks.md contract in `references/artifacts/templates-and-status.md`
- keep the canonical phase structure, stable `taskNNN` ids, explicit dependencies, and truthful specialist metadata
- treat adjacent product docs as scope inputs, not as text to rewrite or reinterpret beyond available evidence
- use decomposition only as needed to make the task plan executable; leave broader package restructuring to `reshape-tasks` or full-package modes
