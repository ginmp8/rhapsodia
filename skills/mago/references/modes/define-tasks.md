# Define Tasks Mode

## Canonical Rules

- Resolve one canonical registry-backed package under `BOARD_ROOT/specs/<spec_id>/`.
- Create or reconcile `tasks.md` only.
- Product docs, manifest, registry identity/dependencies/handoff, generated views, and execution state are read-only.

## Task Definition Workflow

1. Load directly relevant product scope, discovery evidence, technical design, validation plan, package docs, and repository facts.
2. Confirm enough product/technical context exists to define executable work.
3. Create `tasks.md` through the template/scaffold when absent; otherwise reconcile it conservatively.
4. Follow `references/artifacts/templates-and-status.md`, `references/planning-execution-handoff.md`, and `references/specialist-spellbook.md`.
5. Validate the artifact/package and stop once tasks are concrete, dependency-safe, and aligned with current scope.

## Boundaries

- do not create or alter PRD, notes, validation, manifest, registry, generated views, or execution evidence;
- do not infer execution progress, completion, rollout state, or runtime blockers;
- do not redefine product intent or architecture to make task definition easier;
- if product scope or design is insufficient, stop or switch to the matching product/full-package mode.

## Task Focus

- create the smallest truthful five-phase task plan;
- keep stable `taskNNN`, explicit dependencies, phase-correct task types, proportional reasoning, specialist metadata, concrete validation, and expected results;
- execution-required tasks are valid planning outputs and must be handed to MAGIA rather than marked blocked merely because code is required;
- leave broad package restructuring to `reshape-tasks` or full-package modes.
