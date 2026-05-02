# Prepare Define Mode

## Canonical Rules

- `BOARD_ROOT` is required to read spec-catalog.yaml, define-queue.yaml, and linked discovery artifacts.
- The selected queue entry package path is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected queue entry.
- Seed only the selected package under `BOARD_ROOT/specs/<spec_id>/`.

## When to Use It

Use this mode after `order` when define-queue.yaml already exists and you want to seed define-compatible package artifacts from the ordered handoff instead of starting `define` from a blank package.

This mode is the bridge from `order` to ordinary downstream package authoring.

## Preparation Workflow

1. Select exactly one queue entry whose `handoff_status` is `ready_for_prepare_define`.
2. Load the matching spec-catalog.yaml entry, linked discovery candidate docs, and only the directly relevant repository code or tests needed to preserve truth.
3. Apply the matching downstream define contract for the queue entry's `downstream_mode`, then seed only the artifacts justified by `seed_artifacts`.
4. Create or reconcile the selected package path under `BOARD_ROOT/specs/<spec_id>/` from [../canonical-paths.md](../canonical-paths.md) conservatively so the result is compatible with the later downstream mode.
5. Stop once the package starter is truthful and downstream-ready; leave unsupported artifacts for later ordinary define/refine work.

## Boundaries

- do not invent scope, tasks, ordering, execution history, or completion claims just to complete a package skeleton
- never create artifacts outside `BOARD_ROOT`
- inside `BOARD_ROOT`, do not create artifacts outside the queue entry's declared `seed_artifacts` set unless current repository truth now justifies the smaller ordinary downstream mode directly
- do not widen the selected spec beyond the queue entry and linked discovery evidence
- if the queue entry is stale or contradicted by current evidence, block and record the conflict in the seeded package instead of silently rewriting the handoff

## Seeding Rules

- always keep the seeded package aligned with spec-catalog.yaml, define-queue.yaml, and linked discovery candidate docs
- create every seeded template-backed artifact through scripts/write_artifact_scaffold.py <artifact-path> or a narrower local script when one exists
- seed manifest.yaml when identity, classification, and traceability are already justified
- seed notes.md when discovery findings, blockers, open questions, or source mapping need to survive into downstream define work
- seed prd.md, validation.md, or tasks.md only when the queue entry explicitly includes them and current evidence already supports them honestly
- after this mode finishes, continue with the queue entry's `downstream_mode` for ordinary package authoring
