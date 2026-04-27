# Reshape Tasks Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- Task reshaping stays inside the selected package path under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern because task reshaping remains package-local.
- Restrict task reshaping to {BOARD_ROOT}/specs/<spec_id>/tasks.md and directly supporting package files when needed for truth.

## When to Use It

Use this mode when remaining task planning is too broad, tangled, or under-shaped for safe execution.

Split tasks when they are:

- too large for one bounded execution pass
- vague about the concrete change required
- mixing multiple concerns
- spanning too many boundaries without checkpoints
- missing clear validation or expected outcomes
- blocked on hidden prerequisites

## Splitting Rules

Split by:

- outcome
- artifact
- boundary
- prerequisite
- validation responsibility

Do not fragment work into administrative noise.

Prefer the smallest task size that still produces a meaningful, reviewable outcome.

## Task Contract

- follow the canonical tasks.md contract in [../artifacts/templates-and-status.md](references/artifacts/templates-and-status.md)
- keep the existing five-phase sequence intact while making broad work execution-ready
- do not invent placeholder tasks; every retained or added task must produce evidence, code, docs, or an explicit repository-truth confirmation
- when additional bounded work appears, append new `taskNNN` ids into the existing semantically correct phase
- when the work represents a new material execution wave after the current spec is effectively complete, create another spec instead of another phase cycle
- when decomposition introduces new task ids, expect matching `Execution Log` subsections in notes.md once those tasks start execution
- never repurpose a previous task's execution history to a different task id

## Bounded Refinement Tasks

Add a bounded refinement task only when all are true:

1. the same initiative continues under the same PRD
2. future work is still too broad or under-specified
3. a later docs-only pass will materially improve execution quality
4. the refinement stays bounded to the same spec root

Do not use `reshape-tasks` to postpone already-clear planning work.

## Reasoning Guidance

- default to `low` or `medium`
- use `high` only for real architecture or scope-boundary decisions and `xhigh` only for truth-critical or recovery-critical planning boundaries
- if a task appears to need `high` only because it is broad, split it further

## Quality Bar

Before finishing, verify that:

- the initiative boundary stayed stable
- the five-phase structure stayed intact
- there is still only one canonical phase sequence in the file
- every phase has at least one bounded, truthful task
- broad work became execution-ready units
- tasks are dependency-safe, testable, and not fragmented into noise
- reasoning is proportional
- specialist metadata is sparse and useful
- validation stays aligned with the reshaped work
