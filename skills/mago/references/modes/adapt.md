# Adapt Mode

## Canonical Rules

- `BOARD_ROOT` is required for any adapted planning package and must resolve to the canonical year/cycles layout.
- When adaptation targets one selected spec package, use `BOARD_ROOT/specs/<spec_id>/` with a matching `BOARD_ROOT/registry/<spec_id>.yaml` record.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive selected registry/package paths from the canonical pattern when one selected spec package is in scope.
- Do not adapt artifacts outside the resolved operational roots.
- Old layouts are read-only source material. Adaptation writes only the canonical model and never maintains a second active tree.

## When to Use It

Use this mode when planning docs already exist but are outside the MAGO structure or have drifted enough that the first task is normalization, not ordinary refinement.

After adaptation, continue later work with the smallest ordinary mode that matches the result: `refine`, `refine-product`, or `refine-tasks`.

## Adaptation Workflow

1. Load only the existing docs, discovery artifacts, source identity evidence, and repository facts needed to reconstruct current planning truth.
2. Classify the smallest truthful target shape:
   - full package: registry entry, manifest.yaml, prd.md, optional technical-design.md, tasks.md, notes.md, validation.md
   - product-only: registry entry when identity is required, prd.md, notes.md, and optional validation.md
   - tasks-only: existing registry-backed package plus tasks.md
   - blocked partial adaptation when current evidence is still too contradictory or incomplete
3. Open references/artifacts/templates-and-status.md for canonical structure. Open ../markdown-writing.md for changed Markdown artifacts, ../specialist-spellbook.md only when tasks are in scope, and use local scripts for identity creation, template-backed writes, normalization, and validation whenever they exist.
4. Map source identities and paths into `imported_from` or traceability fields; do not reuse legacy counters or semantic versions as new physical IDs.
5. Normalize the existing material into the chosen target shape conservatively.
6. Stop once the package is MAGO-compatible enough for later normal modes without inventing unsupported structure.

## Boundaries

- do not invent new scope, dependencies, ordering, execution progress, or completion claims
- do not create tasks.md unless the existing docs and repository truth already support an executable task plan
- do not create completed tasks only to fill a template or preserve chronology; keep unsupported history in non-task notes or auxiliary docs instead
- do not discard useful non-canonical docs when they still carry truthful context; keep them as read-only source evidence or fold only supported facts into canonical artifacts
- do not widen the initiative boundary just because the legacy docs are messy
- do not operate indefinitely on a legacy layout after canonical identity has been created

## Adaptation Rules

- preserve meaning first; normalize structure second
- prefer the smallest truthful target shape instead of forcing a full package
- if the material only supports product framing, adapt to product-only and omit tasks.md
- if the material includes architecture design, contracts, migration shape, or production-readiness concerns, adapt those facts into technical-design.md only when they are specific enough to remain truthful
- if the material supports executable tasks and the package boundary is already justified, adapt or create tasks.md using the canonical task contract
- if the package already contains canonical MAGO files with drift, reconcile them instead of rebuilding from scratch
- when tasks are in scope, use stable `taskNNN` ids and do not backfill completed tasks without explicit documentary or repository evidence
- create or reconcile cycle/registry/package YAML only when identity and state values are justified by source docs or repository truth
- create new cycle/spec IDs atomically; preserve source IDs only as traceability metadata
- if contradictory sources cannot be reconciled honestly, block and record the conflict explicitly in notes.md when it is in scope; otherwise keep it explicit in the touched artifact
