# Refine Mode

## Canonical Rules

- `BOARD_ROOT` is required for catalog alignment and package traceability.
- The selected spec package path is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected spec package.
- Refine only the selected package under `BOARD_ROOT/specs/<spec_id>/` unless repository truth forces a bounded board-level correction.

## Refinement Workflow

1. Read the current package first.
2. Identify what is still correct and preserve it.
3. Correct only the bounded planning gaps justified by current repository truth.
4. Reconcile touched files so the package is internally consistent again.
5. Stop once the package is truthful, stable, and execution-ready.

## Core Rules

- preserve DONE history
- keep the smallest safe documentation change
- keep the PRD stable unless a real contradiction or changed constraint forces correction
- keep technical-design.md stable unless architecture truth, contract shape, security posture, rollback, observability, or integration boundaries changed
- update only the files touched by the changed planning truth
- do not widen the initiative boundary

## Task Refinement

When refining tasks.md:

- follow the canonical tasks.md contract in [../artifacts/templates-and-status.md](references/artifacts/templates-and-status.md)
- preserve or restore the canonical minimum phase coverage for every phase
- preserve the existing five-phase sequence, phase goals, exit criteria, and stable global `taskNNN` ids
- preserve or create a bounded confirmation task instead of leaving a phase empty
- preserve completed tasks unless they are demonstrably false
- keep checkbox format
- keep `Reasoning` proportional and keep `Why this reasoning is sufficient` explicit
- do not collapse phases or remove a phase heading just because its work is only confirmatory
- do not add a second `Phase 1 ... Phase 5` block or `Phase 6+`; insert bounded new tasks into the existing matching phase
- if new work would represent a new material delivery slice after the current spec is effectively complete, prefer creating another spec

When refining notes.md:

- preserve the canonical notes sections
- preserve `Execution Log`
- preserve task subsections in the form `### taskNNN - <short title>`
- do not delete truthful prior execution history
- keep execution-log field labels in canonical order and use `none` when a required field is intentionally empty
- reconcile stale titles, statuses, follow-ups, and referenced context docs only when repository truth requires it
- if a task was split, keep prior history under the original task and create new subsections only for the new task ids

When refining technical-design.md:

- preserve the canonical heading set and front matter
- reconcile only design claims affected by current evidence
- keep implementation code, CLI runbooks, and execution evidence out of the design
- update `Open Questions` instead of inventing missing security, monitoring, rollback, or contract details

## Bounded Refinement Tasks

Add a bounded refinement task only when all are true:

1. the same initiative continues under the same PRD
2. future work is still too broad or under-specified
3. a later docs-only pass will materially improve execution quality
4. the refinement stays bounded to the same spec root

Do not use refinement to postpone already-clear planning work.

## Reasoning Guidance

- default to `low` or `medium`
- use `high` only for real architecture or scope-boundary decisions and `xhigh` only for truth-critical or recovery-critical planning boundaries
- if a task appears to need `high` only because it is broad, decompose it further

## Quality Bar

Before finishing, verify that:

- the initiative boundary stayed stable
- the PRD changed only if a real contradiction required it
- the five-phase structure remained intact
- there is still only one canonical phase sequence in the file
- every phase still has at least one bounded, truthful task
- tasks remain execution-ready and dependency-safe
- reasoning is proportional
- specialist metadata is sparse and useful
- validation stays aligned with the refined package
- technical design stays aligned with PRD, tasks, validation, and notes when present
