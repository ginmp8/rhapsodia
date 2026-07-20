# Adapt Mode

## Purpose

Translate old-layout or drifted planning into the smallest truthful canonical shape. Adapt is a one-way normalization flow; old layouts remain read-only source evidence, not an alternative active model.

## Canonical Rules

- Resolve or create exactly one canonical cycle and, when package work is needed, one registry-backed spec identity.
- Keep all writes inside the canonical cycle/package roots.
- Preserve source identifiers and paths as import metadata or traceability, never as active canonical IDs.

## Adaptation Workflow

1. Load only source documents, discovery artifacts, execution evidence, and repository facts needed to reconstruct current planning truth.
2. Classify the smallest truthful target shape: full package; product-only; tasks-only; or blocked partial adaptation.
3. Create cycle/spec identity atomically only when the target identity does not already exist.
4. Preserve meaning first and normalize structure second.
5. Use canonical templates, task contracts, ownership rules, and validators.
6. Reconcile package identity without rewriting MAGIA-owned evidence.
7. Stop when the canonical target is sufficient for later `refine`, `refine-product`, or `refine-tasks` without inventing unsupported structure.

## Boundaries

- do not invent scope, dependencies, priority, handoff readiness, execution progress, or completion;
- do not create tasks unless existing evidence supports an executable task plan;
- do not create completed tasks to fill templates or preserve chronology;
- do not discard useful noncanonical context; retain it as read-only auxiliary evidence or fold only supported facts into canonical artifacts;
- do not import multiple cycles/specs in one pass unless explicitly bounded;
- if identity mapping or source precedence is ambiguous, record the contradiction and stop.

## Adaptation Rules

- prefer the smallest truthful target instead of forcing a full package;
- product-only evidence produces product-only artifacts;
- specific architecture/contracts/migration/operability evidence may populate technical design;
- task IDs remain stable and completed history requires documentary/runtime evidence;
- existing canonical files are reconciled rather than rebuilt;
- old execution sections route to MAGIA ADAPT and are not rewritten as MAGO-authored proof;
- canonical drift repair is limited to invalid paths, missing registry/package linkage, stale handoff fields, inconsistent immutable IDs, or misplaced generated aggregates.
