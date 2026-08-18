# MAGO Operating Rules

Use this reference when a request is close to MAGO scope but has ambiguous ownership, mixed planning/execution intent, or unclear artifact boundaries.

## Ownership Rules

MAGO owns planning records that live under the resolved canonical cycle root. It does not own implementation code, runtime execution evidence, delivery-governance reports, release notes, portfolio artifacts, or informal documentation outside the canonical board tree.

When a request contains both planning and execution, complete only the planning-safe portion. The final response must explicitly hand off execution work rather than silently continuing past the boundary.

## Canonical Write Rules

- Resolve the canonical `BOARD_ROOT` before the first write.
- Create cycle/spec identities only through the atomic identity script.
- Write one independent registry record per spec; do not coordinate identity through a shared counter.
- Do not create a second board tree when a canonical one already exists.
- Do not write planning artifacts into root-level docs, temporary folders, ad hoc paths, or legacy version directories.
- Do not hand-edit generated spec-catalog.yaml or define-queue.yaml projections; render them outside `BOARD_ROOT`.
- Preserve immutable IDs, existing truthful history, MAGIA evidence, and source traceability.
- Prefer updating an existing canonical registry/package artifact over creating a duplicate.
- Record missing facts as blockers, assumptions, or open questions inside the relevant planning artifact.

## Mode Discipline

Select one primary mode. A run can read supporting artifacts from adjacent phases, but it must not produce outputs from another primary mode unless the selected mode explicitly owns that transition or the stages run sequentially with separate validation outcomes.

Examples:

- discovery can produce discovery candidates, but not registry records or full spec packages.
- order can create/reconcile registry records and external generated views, but not write package PRDs.
- prepare-define can seed one registered package, but not fill unsupported product or task content.
- define-product must not modify task plans.
- define-tasks must not modify product docs.
- technical-design must not become implementation code, runbook, or runtime evidence.

## Evidence Standard

Planning claims must trace to at least one of these sources:

- repository inspection;
- existing canonical cycle, registry, package, or MAGIA evidence artifacts;
- user-provided roadmap or product evidence;
- accepted assumptions explicitly recorded in the artifact;
- validator output for structural claims.

Distinguish observed, inferred, planned, and measured claims. Do not transform guesses into identity, status, priority, dependency, order, handoff readiness, completion, approval, or specialist assignments.

## Planning/Execution Boundary

Planning authority is not an implementation prohibition. Define executable downstream tasks when scope and validation are credible. Do not mark work blocked solely because code, configuration, tests, migration, or technical documentation are required; hand it to MAGIA and reserve blockers for missing scope, files, dependencies, credentials, evidence, or validation paths.

## Handoff Language

When stopping at the planning boundary, include:

- the selected MAGO mode completed;
- resolved board/cycle/spec identity and paths;
- artifacts changed and validators run;
- what was intentionally not done;
- which execution, governance, or code workflow should take over;
- any blocker that must be resolved before that handoff.

Never imply implementation or runtime validation occurred when it did not.
