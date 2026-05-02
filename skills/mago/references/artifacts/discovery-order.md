# Discovery and Order Artifacts

Use this reference when `discovery`, `order`, or `prepare-define` creates or reconciles upstream artifacts.

## Discovery Root Layout

All layouts below derive from `BOARD_ROOT` in `references/canonical-paths.md`.

```text
BOARD_ROOT/
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

```text
BOARD_ROOT/
  spec-catalog.yaml
  define-queue.yaml
```

## define-queue.yaml

- purpose: explicit handoff from `order` to downstream define preparation
- required keys: `schema_version`, `cycle_version`, `entries`
- each entry needs `spec_id`, `feature_key`, `title`, `handoff_status`, `downstream_mode`, `package_shape`, `source_candidates`, `seed_artifacts`, `define_target`, and `blockers`
- populate `entries` with `scripts/update_template_lists.py <define-queue.yaml> --data <payload.yaml>`; do not hand-shape queue entries
- set `define_target` to the repository-relative package path under `BOARD_ROOT/specs/<spec_id>/`
- use `handoff_status` only from `ready_for_prepare_define`, `blocked`, or `needs_discovery`
- use `downstream_mode` only from `define`, `define-product`, or `define-tasks`
- use `package_shape` only from `full`, `product_only`, or `tasks_only`
- use `seed_artifacts` only from canonical package files: manifest.yaml, prd.md, technical-design.md, tasks.md, notes.md, validation.md

## Cross-Stage Invariants

- every `candidate_id` in discovery-index.yaml must be unique
- every `candidate_doc` listed in discovery-index.yaml must exist under `BOARD_ROOT`
- every `source_candidates` path in define-queue.yaml must exist and point to a discovery candidate doc under `BOARD_ROOT`
- every `spec_id` in define-queue.yaml must exist in spec-catalog.yaml
- never let define-queue.yaml claim a downstream mode or seed artifact set that the linked discovery evidence cannot already justify
