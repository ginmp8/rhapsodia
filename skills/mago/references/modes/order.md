# Order Mode

## Canonical Rules

- `BOARD_ROOT` is required for registry reconciliation and must contain `cycle.yaml`.
- Use prompt-provided `BOARD_ROOT` when present; otherwise derive it from canonical-paths.md.
- No separate spec package root is active in `order`; future package targets are derived under `BOARD_ROOT/specs/<spec_id>/`.
- Each ordered item is an independent `BOARD_ROOT/registry/<spec_id>.yaml` source-of-truth record.
- Do not create or hand-edit shared spec-catalog.yaml or define-queue.yaml files under `BOARD_ROOT`; render deterministic external projections only when needed.

## Discovery Input Rules

- treat discovery artifacts as upstream evidence and traceability, not as identity or sequencing truth
- never import `spec_id`, immutable ULID identity, priority, dependency order, or `feature_version` from discovery artifacts without independent planning evidence
- reuse a stable provisional `feature_key` only when the capability boundary remains supported

## Ordering Workflow

1. Work only inside the resolved `BOARD_ROOT` from `references/canonical-paths.md`.
2. Load cycle.yaml, discovery-index.yaml, and only the candidate docs referenced by the candidates being ordered.
3. Load existing registry records so identity, dependencies, status, supersession, and handoff truth are preserved.
4. Deduplicate discovery candidates by capability boundary and stable `feature_key`.
5. Preserve existing `spec_id`, dependency relationships, priority, `order_hint`, and define handoff truth unless stronger evidence proves correction is necessary.
6. Create new specs only when the work is materially distinct or a new package is genuinely needed.
7. Create identity atomically with `scripts/create_planning_identity.py spec`; never coordinate through a shared sequence counter.
8. Assign priority and optional `order_hint` conservatively; dependency topology remains authoritative.
9. Keep `depends_on_features` and `depends_on_specs` distinct.
10. Reconcile the registry handoff for every ordered spec so downstream define preparation is explicit.
11. Validate duplicate active features, missing dependencies, cycles, and registry/package drift with `scripts/validate_repo_board.py`.
12. Render external catalog/queue projections only for inspection or CI with `scripts/render_registry_views.py`.

## Catalog Shape

The canonical catalog is the set of independent registry records. Generated `spec-catalog.yaml` is a read-only projection of this shape.

### Registry Shape

- identity fields: `kind`, `spec_id`, `spec_uid`, `cycle_id`, `feature_key`, `created_at`
- planning fields: `feature_version`, `title`, `type`, `classification`, `status`, `priority`, `order_hint`
- dependency fields: `depends_on_features`, `depends_on_specs`
- lifecycle fields: `supersedes`, `superseded_by`
- handoff fields: `status`, `downstream_mode`, `package_shape`, `source_candidates`, `seed_artifacts`, `blockers`
- optional import traceability: `imported_from`
- use `type: fix` only for bugfix-style work; otherwise default to `type: feature`

## Define Handoff Shape

- handoff `status`: `ready_for_prepare_define`, `blocked`, or `needs_discovery`
- `downstream_mode`: `define`, `define-product`, or `define-tasks`
- `package_shape`: `full`, `product_only`, or `tasks_only`
- `source_candidates`: repository-relative candidate paths under the active cycle root
- `seed_artifacts`: canonical package files only
- package target is derived as `BOARD_ROOT/specs/<spec_id>/`; it is not a second identity field

## Catalog Authoring Rules

Catalog authoring means creating or reconciling independent registry records; it never means hand-editing a shared aggregate.

### Registry Authoring Rules

- create identities and initial registry records with scripts/create_planning_identity.py; use templates directly only as read-only structural references when no script can perform the needed check
- keep existing truthful values when a registry record already established them
- replace placeholders and examples with real values derived from discovery evidence and repository truth
- never reuse an existing ULID for a different cycle or spec
- do not copy template literals for identity, status, priority, dependency, handoff, or feature version blindly
- do not mutate another worker's unrelated registry record while ordering one candidate

## Ordering Heuristics

- broader enabling work may come before dependent slices
- stronger evidence and clearer entrypoints win ties
- preserve existing dependency and presentation order when it is still coherent
- do not force weak discovery evidence into the registry
- set `handoff.status: ready_for_prepare_define` only when the ordered discovery artifacts already justify a stable downstream package shape
- if the boundary is too ambiguous, stop and keep ordering blocked rather than inventing structure
- duplicate active `feature_key` values are semantic conflicts to resolve, not sequence collisions to renumber

## Output Rules

- ordering touches only the selected registry records and, when justified, cycle planning metadata; it does not create spec folders or implementation output
- generated catalog/queue files are disposable external views and never canonical outputs
- if registry records and handoffs are already coherent, keep them stable and make only justified bounded corrections
