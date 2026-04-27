# Common Planning

## Canonical Model

- `board_id`: required dynamic repository board segment under `docs/boards/`
- `cycle_version`: required dynamic cycle version segment used in both the canonical path and artifact metadata
- `spec_id`: stable sequential spec id, formatted as `specNNN`
- `feature_key`: stable functional identity, lowercase kebab-case
- `feature_version`: semantic version for the capability or fix
- never use `feature_key` as the spec identifier
- never use semantic versioning for roadmap order
- preserve `spec_id` once assigned unless repository truth requires a rare correction

## Operational Roots

- load canonical defaults from [references/canonical-paths.md](references/canonical-paths.md)
- `BOARD_ROOT` is the active board root for the run
- use prompt-provided `BOARD_ROOT` when present; otherwise derive it from the canonical defaults with concrete `board_id` and `cycle_version`
- when the selected mode operates on one package, derive its package path from `BOARD_ROOT` with concrete `spec_id`
- all derived planning paths must resolve from `BOARD_ROOT`; do not introduce parallel aliases with different meaning

## Layout

```text
BOARD_ROOT/
  discovery-state.json
  discovery-index.yaml
  candidates/
    <candidate_id>.md
  spec-catalog.yaml
  define-queue.yaml
  specs/
    <spec_id>/
      manifest.yaml
      prd.md
      technical-design.md
      tasks.md
      notes.md
      validation.md
```

`<board_id>` and `<cycle_version>` are mandatory dynamic path segments for canonical board resolution. `spec_id` is additionally required for canonical spec resolution. If neither prompt overrides nor repository evidence establishes the needed operational roots, block instead of creating planning documentation outside `BOARD_ROOT`.

- all modes write under `BOARD_ROOT`
- full-package modes normally use the whole layout above; technical-design.md is optional and used only when architecture or contract alignment is material
- spec folders may also contain auxiliary docs local to the same spec root, such as contracts, runbooks, or adoption notes, when they clarify downstream execution without replacing the canonical files
- `define-product` and `refine-product` may work on a documentation-only subset under the selected spec root: prd.md, notes.md, and optional validation.md
- `define-tasks` and `refine-tasks` may work on tasks.md only under the selected spec root
- discovery work uses `BOARD_ROOT` with discovery-state.json, discovery-index.yaml, and `candidates/`
- root-level cycle folders, ad hoc `docs/mago/`, and planning docs outside `BOARD_ROOT` are noncanonical

## Source of Truth

- `BOARD_ROOT`: mandatory location boundary for every generated planning artifact
- spec-catalog.yaml: `order`, `spec_id`, `feature_key`, dependency summary, high-level status, `feature_version`, `cycle_status`
- define-queue.yaml: order-to-define handoff, downstream mode, package shape, source discovery candidates, seedable artifacts, and blockers
- manifest.yaml: local identity, classification, `status`, `phase`, `source_of_truth`, traceability, and optional `last_execution`
- prd.md, technical-design.md, notes.md, validation.md, and when present tasks.md: detailed planning meaning
- technical-design.md: optional architecture, data-flow, contract, security, monitoring, rollback, and implementation-approach alignment for the selected spec
- tasks.md and execution-labeled fields form downstream execution contract when tasks are in scope

## Dependencies and Status

- `depends_on_features`: list of `feature_key`
- `depends_on_specs`: list of `spec_id`
- task `Dependencies`: task-local prerequisites inside tasks.md

Catalog `status` values:

- `planned`
- `in_progress`
- `done`
- `cancelled`

Catalog `cycle_status` values:

- `planned`
- `in_progress`
- `done`
- `cancelled`

Manifest `phase` values:

- `define`
- `execute`
- `review`
- `done`

## Product-Only Modes

- `define-product` and `refine-product` touch only prd.md, notes.md, and optional validation.md
- do not create or alter tasks.md, reorder catalog state, or infer execution state
- keep notes.md product-only: omit `Specialist Rationale` and `Execution Log` unless truthful existing sections must be preserved in place

## Task-Only Modes

- `define-tasks` and `refine-tasks` touch only tasks.md
- use those modes only when product scope and package boundary are already justified
- do not alter prd.md, notes.md, validation.md, manifest.yaml, or spec-catalog.yaml, and do not infer execution state

## Technical Design Mode

- `technical-design` touches only technical-design.md unless a bounded consistency correction to notes.md or validation.md is explicitly justified by the same evidence
- use this mode when the selected spec needs architecture, contract, migration, observability, security, rollback, or option-alignment detail before execution
- do not create implementation task decomposition, execution steps, repository changes, or validation evidence in technical-design.md
- if current evidence is thin, create a small design with explicit unknowns and open questions instead of inventing architecture
- size the design from evidence: `small` for a narrow low-risk boundary, `medium` for multiple touched boundaries or new contracts, `large` for multi-system, migration, security, compliance, or production-risk work, and `unknown` when sizing itself needs verification
- verify technical claims through selected package evidence, repository code/tests/configs, repository docs, and official dependency docs before writing them as facts; unresolved claims belong in `Open Questions`

## Adaptation Mode

- `adapt` normalizes pre-existing non-MAGO or drifted planning docs into the smallest truthful MAGO-compatible shape: full-package, product-only, tasks-only, or blocked partial adaptation
- after adaptation, continue with `refine`, `refine-product`, or `refine-tasks`

## Define Preparation Mode

- `prepare-define` reads define-queue.yaml, spec-catalog.yaml, and linked discovery evidence to seed only the justified downstream artifacts
- after `prepare-define`, continue with the queue entry's downstream mode: `define`, `define-product`, or `define-tasks`

## Planning Boundary

- `mago` plans, refines, and documents; it does not implement product code or run execution workflows
- execution-labeled headings and fields such as `Execution Rules`, `Execution Log`, task `Validation`, or manifest `phase: execute` are downstream artifact schema, not `mago` operating instructions
- only reflect execution progress, completion, or blockers when repository evidence or existing planning truth already supports that state
- if the user request crosses into implementation, stop at planning output instead of switching into execution work

## Planning Rules

- preserve truthful history and discovery traceability
- prefer bounded updates over rewrites
- underdefined work is normal: derive the smallest coherent artifact set that current evidence supports
- every new or changed artifact must trace back to repository truth, discovery evidence, or a necessary downstream-enabling clarification
- record assumptions, risks, and open questions in notes.md when it is in scope; otherwise keep them explicit in the touched planning artifact instead of pretending certainty
- do not ask for clarification during unattended loops
- continue conservatively only when the result remains honest and downstream-enabling
- block instead of inventing false boundaries, unsupported dependencies, arbitrary order, or unsupported status claims

## Template Rules

- templates are structural references only and script inputs first
- use scripts/write_artifact_scaffold.py <artifact-path> or a narrower local script whenever creating, refreshing, or normalizing a template-backed artifact
- after writing or editing any template-backed MAGO artifact, use scripts/validate_artifact.py <artifact-path> or the narrower local validator before relying on manual review
- replace placeholders and examples with repository-truth values before treating an artifact as complete
- preserve real values already established by the active catalog, selected package, discovery evidence, or repository truth
- never copy dynamic values such as `cycle_version`, `order`, `spec_id`, `feature_key`, `feature_version`, `type`, `classification`, `status`, or `phase` blindly from template text

## Cross-Artifact Consistency

- bootstrap a missing catalog inside the resolved `BOARD_ROOT` with `cycle_version: 01.00.00` and `cycle_status: planned` unless repository truth already establishes another starting point
- any `taskNNN` referenced by task `Dependencies`, notes.md execution-log subsections, or `manifest.yaml.last_execution.task_id` must exist in tasks.md
- canonical notes.md `Execution Log` `Status` values are `not_started`, `in_progress`, `blocked`, and `done`
- canonical `manifest.yaml.last_execution` keeps `task_id` required and `date`, `summary`, and `files_changed` optional; preserve truthful legacy extra keys conservatively, but do not invent new noncanonical keys
- if no task has truthfully executed yet, omit `manifest.yaml.last_execution`
- when task ids split or new ids are introduced, preserve old truthful history under the old id and add new execution-log subsections only for the new ids

## Naming Rules

Keep directory names, file names, ids, YAML keys, and enum values lowercase. `board_id` and `cycle_version` must be safe POSIX path segments: no slashes, backslashes, empty segments, `.` segments, or `..` traversal.
