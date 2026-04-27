# Order Mode

## Canonical Rules

- `BOARD_ROOT` is required for catalog and queue reconciliation.
- Use prompt-provided `BOARD_ROOT` when present; otherwise derive it from `references/canonical-paths.md`.
- No separate spec root is active in `order`; queued spec targets are derived package paths under `BOARD_ROOT/specs/<spec_id>/`.
- Keep spec-catalog.yaml and define-queue.yaml under `BOARD_ROOT` only.

## Discovery Input Rules

- treat discovery artifacts as upstream evidence and traceability, not as sequencing truth
- never import `spec_id`, `order`, `cycle_version`, or `feature_version` from discovery artifacts

## Ordering Workflow

1. Work only inside the resolved `BOARD_ROOT` from [../canonical-paths.md](references/canonical-paths.md).
2. Locate the highest open catalog in that resolved `BOARD_ROOT` whose `cycle_status` is `planned` or `in_progress`.
3. If no open catalog exists in that resolved `BOARD_ROOT`, create the bootstrap initial catalog there: `cycle_version: 01.00.00`, `cycle_status: planned`.
4. Load discovery-index.yaml and the candidate docs referenced by the candidates you are ordering.
5. Load the current spec-catalog.yaml and define-queue.yaml when they exist.
6. Deduplicate discovery candidates by capability boundary and stable `feature_key`.
7. Preserve existing `spec_id`, `order`, dependency relationships, and define handoff truth unless evidence proves they are wrong.
8. Create new specs only when the work is materially distinct or a new package is genuinely needed.
9. Assign the next available `specNNN`.
10. Assign `order` conservatively and keep insertion gaps when useful.
11. Keep `depends_on_features` and `depends_on_specs` distinct.
12. Create or reconcile a define-queue.yaml entry for every ordered spec so downstream define preparation is explicit.

## Catalog Shape

- catalog keys: `schema_version`, `cycle_version`, `cycle_status`, `specs`
- each spec entry needs `order`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `depends_on_features`, `depends_on_specs`, `status`, `feature_version`
- use `type: fix` only for bugfix-style work; otherwise default to `type: feature`

## Define Handoff Shape

- define-queue.yaml keys: `schema_version`, `cycle_version`, `entries`
- each queue entry needs `spec_id`, `feature_key`, `title`, `handoff_status`, `downstream_mode`, `package_shape`, `source_candidates`, `seed_artifacts`, `define_target`, and `blockers`
- `define_target` must be the repository-relative package path under `BOARD_ROOT/specs/<spec_id>/`
- use `downstream_mode` only from `define`, `define-product`, or `define-tasks`
- use `package_shape` only from `full`, `product_only`, or `tasks_only`
- use `handoff_status` only from `ready_for_prepare_define`, `blocked`, or `needs_discovery`

## Catalog Authoring Rules

- when creating a missing catalog or queue, use scripts/write_artifact_scaffold.py <artifact-path> first; use template text directly only as a read-only reference when no script can perform the needed operation
- keep existing truthful values when the catalog already established them
- replace placeholders and examples with real values derived from discovery evidence and repository truth
- use the bootstrap initial cycle only when no cycle exists yet
- do not copy template literals for `cycle_version`, `order`, `spec_id`, `status`, or `feature_version` blindly

## Ordering Heuristics

- broader enabling work may come before dependent slices
- stronger evidence and clearer entrypoints win ties
- preserve existing order when it is still coherent
- do not force weak discovery evidence into the catalog
- set `handoff_status: ready_for_prepare_define` only when the ordered discovery artifacts already justify a stable downstream package shape
- if the boundary is too ambiguous, stop and keep ordering blocked rather than inventing structure

## Output Rules

- ordering touches only spec-catalog.yaml and define-queue.yaml inside the resolved `BOARD_ROOT`; it does not create spec folders or implementation output
- if the catalog and define queue are already coherent, keep them stable and make only justified bounded corrections
