# Adapt Mode

## Canonical Rules

- `BOARD_ROOT` is required for any adapted planning package.
- When adaptation targets one selected spec package, use the package path under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern when one selected spec package is in scope.
- Do not adapt artifacts outside the resolved operational roots.

## When to Use It

Use this mode when planning docs already exist but are outside the MAGO structure or have drifted enough that the first task is normalization, not ordinary refinement.

After adaptation, continue later work with the smallest ordinary mode that matches the result: `refine`, `refine-product`, or `refine-tasks`.

## Adaptation Workflow

1. Load only the existing docs, discovery artifacts, and repository facts needed to reconstruct current planning truth.
2. Classify the smallest truthful target shape:
   - full package: manifest.yaml, prd.md, optional technical-design.md, tasks.md, notes.md, validation.md
   - product-only: prd.md, notes.md, and optional validation.md
   - tasks-only: tasks.md
   - blocked partial adaptation when current evidence is still too contradictory or incomplete
3. Open `references/artifacts/templates-and-status.md` for canonical structure. Open references/markdown-writing.md for changed Markdown artifacts, references/specialist-spellbook.md only when tasks are in scope, and use local scripts for template-backed writes, normalization, and validation whenever they exist.
4. Normalize the existing material into the chosen target shape conservatively.
5. Stop once the package is MAGO-compatible enough for later normal modes without inventing unsupported structure.

## Boundaries

- do not invent new scope, dependencies, ordering, execution progress, or completion claims
- do not create tasks.md unless the existing docs and repository truth already support an executable task plan
- do not create completed tasks only to fill a template or preserve chronology; keep unsupported history in non-task notes or auxiliary docs instead
- do not discard useful non-canonical docs when they still carry truthful context; keep them as auxiliary docs or fold only their supported facts into canonical artifacts
- do not widen the initiative boundary just because the legacy docs are messy

## Adaptation Rules

- preserve meaning first; normalize structure second
- prefer the smallest truthful target shape instead of forcing a full package
- if the material only supports product framing, adapt to product-only and omit tasks.md
- if the material includes architecture design, contracts, migration shape, or production-readiness concerns, adapt those facts into technical-design.md only when they are specific enough to remain truthful
- if the material supports executable tasks and the package boundary is already justified, adapt or create tasks.md using the canonical task contract
- if the package already contains canonical MAGO files with drift, reconcile them instead of rebuilding from scratch
- when tasks are in scope, use stable `taskNNN` ids and do not backfill completed tasks without explicit documentary or repository evidence
- create or reconcile YAML only when identity and state values are already justified by the current docs or repository truth
- if contradictory sources cannot be reconciled honestly, block and record the conflict explicitly in notes.md when it is in scope; otherwise keep it explicit in the touched artifact
