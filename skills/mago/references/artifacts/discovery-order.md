# Discovery and Order Artifacts

Use this reference when `discovery`, `order`, or `prepare-define` creates or reconciles upstream artifacts.

## Discovery Root Layout

All layouts below derive from `BOARD_ROOT` in `references/canonical-paths.md`.

```text
BOARD_ROOT/
  cycle.yaml
  discovery-state.json
  discovery-index.yaml
  candidates/
    <candidate_id>.md
```

## discovery-state.json

- purpose: machine-readable loop state for iterative frontier scanning
- required keys: `schema_version`, `project_root`, `iteration`, `frontier_queue`, `completed_frontiers`, `blocked_frontiers`, `frontier_history`, `file_inventory`
- keep it factual and operational; do not store speculative product scope here
- each `frontier_history` entry should record the bounded batch processed in one iteration and the truthful next frontier decision

## discovery-index.yaml

- required keys: `schema_version`, `discovery_root`, `project_root`, `last_iteration`, `candidates`
- set `discovery_root` to the repository-relative `BOARD_ROOT`
- each candidate entry needs `candidate_id`, `title`, `status`, `candidate_doc`, `frontier`, `core_files`, `triage_confidence`, `boundary_risk`, and `suggested_next_step`
- populate `candidates` with `scripts/update_template_lists.py <discovery-index.yaml> --data <payload.yaml>`; do not hand-shape candidate entries
- optional fields: `provisional_feature_key`, `supporting_files`, `duplicate_of`
- use `status` only from `new`, `updated`, `provisional`, `ready_for_order`, `blocked`, `duplicate`
- use `suggested_next_step` only from `continue_discovery`, `order`, or `drop`

## candidates/<candidate_id>.md

- create a new candidate doc with scripts/write_artifact_scaffold.py <path> --template discovery-candidate.md.template; use the template directly only as a read-only reference when no script can perform the needed check
- keep front matter factual and stable for the candidate boundary
- preserve these sections in order: `Scope Summary`, `Observed Behavior`, `Entry Points`, `Core Files`, `Supporting Files`, `Dependencies and Integrations`, `Open Questions`, `Promotion Decision`
- use repository-relative POSIX paths
- keep evidence concise; detailed excerpts belong in supporting docs only when they materially improve later ordering

## Order Outputs

Canonical order output is one independent registry record per spec. Aggregate catalog and queue files are generated projections only.

### Order Source of Truth

```text
BOARD_ROOT/
  registry/
    <spec_id>.yaml
```

Each registry file owns one ordered spec. Create new identities atomically through `scripts/create_planning_identity.py spec`; do not coordinate through a shared counter or central mutable list.

## registry/<spec_id>.yaml

- purpose: canonical registration and define handoff for one planning item
- required identity fields: `kind`, `spec_id`, `cycle_id`, `feature_key`, `created_at`
- required planning fields: `feature_version`, `title`, `type`, `classification`, `status`, `priority`, `order_hint`
- required dependency fields: `depends_on_features`, `depends_on_specs`
- required lifecycle fields: `supersedes`, `superseded_by`
- required handoff mapping: `status`, `downstream_mode`, `package_shape`, `source_candidates`, `seed_artifacts`, `blockers`
- optional import traceability: `imported_from`
- source candidates must resolve under the active `BOARD_ROOT/candidates/`
- package target is derived as `BOARD_ROOT/specs/<spec_id>/`; do not store a second mutable identity
- use handoff `status` only from `ready_for_prepare_define`, `blocked`, or `needs_discovery`
- use `downstream_mode` only from `define`, `define-product`, or `define-tasks`
- use `package_shape` only from `full`, `product_only`, or `tasks_only`
- use `seed_artifacts` only from canonical package files: manifest.yaml, prd.md, technical-design.md, tasks.md, notes.md, validation.md

## define-queue.yaml

`define-queue.yaml` is a generated read-only view of registry handoff fields, not a writable queue source.

## Generated Views

`scripts/render_registry_views.py` creates external inspection/CI projections:

```text
<output>/spec-catalog.yaml
<output>/define-queue.yaml
```

- templates document the complete generated schemas
- generated views include `cycle_id` and a registry digest
- ordering is deterministic from dependency topology, priority, order hint, creation timestamp, and spec id
- never write generated views under `BOARD_ROOT`
- never hand-edit generated views or synchronize their values back into registry/package state

## Cross-Stage Invariants

- every `candidate_id` in discovery-index.yaml must be unique
- every `candidate_doc` listed in discovery-index.yaml must exist under `BOARD_ROOT`
- every registry `source_candidates` path must exist and point to a discovery candidate doc under `BOARD_ROOT`
- every registry filename and `spec_id` must agree with canonical identity format, and `feature_key` must agree with the ID feature segment
- every package directory must have a matching registry record and matching manifest identity
- every `feature_key` must be unique; distinct specs require distinct feature keys
- every `depends_on_specs` value must resolve to a registry record and the dependency graph must be acyclic
- never let a registry handoff claim a downstream mode or seed artifact set that linked discovery evidence cannot justify
- generated catalog/queue views must reproduce registry state deterministically but remain noncanonical
