# MAGO Operating Rules

Use this reference when a request is close to MAGO scope but has ambiguous ownership, mixed planning/execution intent, or unclear artifact boundaries.

## Ownership Rules

MAGO owns planning records that live under the resolved board root. It does not own implementation code, runtime execution evidence, delivery-governance reports, release notes, portfolio artifacts, or informal documentation outside the canonical board tree.

When a request contains both planning and execution, complete only the planning-safe portion. The final response must explicitly hand off execution work rather than silently continuing past the boundary.

## Canonical Write Rules

- Resolve the board root before the first write.
- Do not create a second board tree when a canonical one already exists.
- Do not write planning artifacts into root-level docs, temporary folders, or ad hoc paths.
- Preserve existing stable ids unless repository truth requires a change.
- Prefer updating an existing canonical artifact over creating a duplicate.
- Record missing facts as blockers, assumptions, or open questions inside the relevant planning artifact.

## Mode Discipline

Select one primary mode. A run can read supporting artifacts from adjacent phases, but it must not produce outputs from another primary mode unless the selected mode explicitly owns that transition.

Examples:

- discovery can produce discovery candidates, but not full spec packages.
- order can update spec catalog and define queue, but not write package PRDs.
- prepare-define can seed package scaffolds, but not fill unsupported product or task content.
- define-product must not modify task plans.
- define-tasks must not modify product docs.

## Evidence Standard

Planning claims must trace to at least one of these sources:

- repository inspection;
- existing canonical planning artifacts;
- user-provided roadmap or product evidence;
- accepted assumptions explicitly recorded in the artifact;
- validator output for structural claims.

Do not transform guesses into status, priority, dependency, completion, or specialist assignments.

## Handoff Language

When stopping at the planning boundary, include:

- the selected MAGO mode completed;
- what was intentionally not done;
- which execution, governance, or code workflow should take over;
- any blocker that must be resolved before that handoff.
