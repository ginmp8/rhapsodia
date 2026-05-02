# Refine Tasks Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- The selected tasks-only package slice is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected package slice.
- Keep task-only refinement inside `BOARD_ROOT/specs/<spec_id>/`.

## Task Refinement Workflow

1. Read the current tasks.md first and preserve what is still true.
2. Load only the adjacent docs and repository facts needed to keep task scope aligned with the current product definition.
3. Tighten or reconcile tasks.md only.
4. Open references/artifacts/templates-and-status.md for the canonical tasks.md contract. Open ../specialist-spellbook.md for task specialist metadata, ../markdown-writing.md for Markdown edits, and use local scripts for template-backed writes, normalization, and validation whenever tasks.md needs template reconciliation.
5. Stop once tasks.md is clearer, internally consistent, and still within the current product scope.

## Boundaries

- do not create or alter prd.md, notes.md, validation.md, manifest.yaml, or spec-catalog.yaml
- do not infer execution progress, completion, blockers, rollout state, or execution history
- do not widen the product boundary or backfill product rationale that belongs in product-only or full-package modes
- if visible contradictions between tasks.md and adjacent docs cannot be resolved truthfully from tasks.md alone, stop or switch to `refine`, `define-product`, or `refine-product`
- if the current task plan is missing essential product context, stop or switch to `refine`, `define-product`, or `refine-product`

## Refinement Focus

- follow the canonical tasks.md contract in references/artifacts/templates-and-status.md
- improve task clarity, dependency safety, phase placement, reasoning proportionality, and specialist metadata
- preserve stable ids, canonical phase order, truthful completed-task history, and the current initiative boundary
- preserve visible cross-artifact task-id compatibility when it can be kept from tasks.md alone; do not invent renumbering or fake history to paper over drift in untouched files
- keep the change set minimal when the current tasks.md is already coherent
