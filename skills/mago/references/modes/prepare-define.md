# Prepare Define Mode

## Canonical Rules

- `BOARD_ROOT` is required to read one registry handoff and its linked discovery artifacts.
- The selected registry record is always `BOARD_ROOT/registry/<spec_id>.yaml`.
- The selected package path is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected registry/package paths from the canonical pattern.
- Seed only the selected package under `BOARD_ROOT/specs/<spec_id>/`.

## When to Use It

Use this mode after `order` when one registry handoff is `ready_for_prepare_define` and you want to seed define-compatible package artifacts from that ordered handoff instead of starting `define` from a blank package.

This mode is the bridge from `order` to ordinary downstream package authoring. Generated define-queue views may be used for inspection, but the registry record remains authoritative.

## Preparation Workflow

1. Select exactly one registry record whose `handoff.status` is `ready_for_prepare_define`.
2. Load the selected registry record, linked discovery candidate docs, and only the directly relevant repository code or tests needed to preserve truth.
3. Apply the matching downstream define contract for the handoff's `downstream_mode`, then seed only the artifacts justified by `seed_artifacts`.
4. Create or reconcile the selected package path under `BOARD_ROOT/specs/<spec_id>/` from `references/canonical-paths.md` conservatively so the result is compatible with the later downstream mode.
5. Ensure manifest identity matches cycle.yaml and the registry record.
6. Stop once the package starter is truthful and downstream-ready; leave unsupported artifacts for later ordinary define/refine work.

## Boundaries

- do not invent scope, tasks, ordering, execution history, or completion claims just to complete a package skeleton
- never create artifacts outside `BOARD_ROOT`
- inside `BOARD_ROOT`, do not create artifacts outside the registry handoff's declared `seed_artifacts` set unless current repository truth now justifies the smaller ordinary downstream mode directly
- do not widen the selected spec beyond the registry record and linked discovery evidence
- if the registry handoff is stale or contradicted by current evidence, block and record the conflict in the registry/package instead of silently rewriting unrelated planning state
- do not hand-edit generated spec-catalog.yaml or define-queue.yaml projections

## Seeding Rules

- always keep the seeded package aligned with cycle.yaml, the selected registry record, and linked discovery candidate docs
- create every seeded template-backed artifact through scripts/write_artifact_scaffold.py <artifact-path> or a narrower local script when one exists
- seed manifest.yaml when identity, classification, and traceability are already justified
- seed notes.md when discovery findings, blockers, open questions, or source mapping need to survive into downstream define work
- seed prd.md, validation.md, or tasks.md only when the registry handoff explicitly includes them and current evidence already supports them honestly
- after this mode finishes, continue with the registry handoff's `downstream_mode` for ordinary package authoring
