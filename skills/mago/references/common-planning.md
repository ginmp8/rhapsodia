# Common Planning

## Canonical Model

- `board_id`: required repository board segment under `docs/boards/`.
- `cycle_version`: required cycle segment used in path and metadata.
- `spec_id`: stable sequential id, `specNNN`; preserve once assigned unless repository truth requires correction.
- `feature_key`: stable lowercase kebab-case functional identity; never use it as `spec_id`.
- `feature_version`: semantic capability/fix version; never use semantic versioning for roadmap order.

## Operational Roots and Layout

Load defaults from `references/canonical-paths.md`. `BOARD_ROOT` is the active boundary; use prompt-provided root when valid, otherwise derive it from concrete `board_id` and `cycle_version`. Package paths derive from `BOARD_ROOT/specs/<spec_id>/`. Do not create parallel aliases.

```text
BOARD_ROOT/
  discovery-state.json
  discovery-index.yaml
  candidates/<candidate_id>.md
  spec-catalog.yaml
  define-queue.yaml
  specs/<spec_id>/
    manifest.yaml
    prd.md
    technical-design.md
    tasks.md
    notes.md
    validation.md
    implementation-notes.md        # MAGIA-owned execution record, when execution exists
    validation-evidence.md         # MAGIA-owned validation evidence, when execution exists
```

Block if required root segments cannot be proven. All modes write under `BOARD_ROOT`. Full packages normally use the package layout; technical-design.md is optional and used only for material architecture/contract alignment. Spec-local auxiliary docs may clarify downstream execution but must not replace canonical files. Product-only modes touch prd.md, notes.md, optional validation.md. Task-only modes touch tasks.md only. Discovery uses discovery-state.json, discovery-index.yaml, and `candidates/`. Root cycle folders, ad hoc `docs/mago/`, and docs outside `BOARD_ROOT` are noncanonical.

## Source of Truth

- `BOARD_ROOT`: mandatory location boundary.
- spec-catalog.yaml: `order`, `spec_id`, `feature_key`, dependencies, status, `feature_version`, `cycle_status`.
- define-queue.yaml: order-to-define handoff, downstream mode, package shape, discovery sources, seedable artifacts, blockers.
- manifest.yaml: identity, classification, planning `status`/`phase`, `source_of_truth`, traceability, optional truthful `last_execution` preserved from MAGIA evidence.
- prd.md, technical-design.md, notes.md, validation.md, tasks.md when present: detailed planning meaning. `implementation-notes.md` and `validation-evidence.md` are MAGIA-owned execution evidence when present.
- technical-design.md: optional selected-spec architecture/data-flow/contract/security/monitoring/rollback/implementation-approach alignment.
- tasks.md plus execution-labeled fields: downstream execution contract, not MAGO execution authority.

## Dependencies and Status

- Dependencies: `depends_on_features` = `feature_key` list; `depends_on_specs` = `spec_id` list; task `Dependencies` = task-local prerequisites.
- Catalog `status` and `cycle_status`: `planned`, `in_progress`, `done`, `cancelled`.
- Manifest `phase`: `define`, `execute`, `review`, `done`.

## Mode Boundaries

- Product-only: `define-product` / `refine-product` touch only prd.md, notes.md, optional validation.md; do not alter tasks.md, catalog order, or execution state. Product-only notes omit execution records. If legacy execution sections are present, run the appropriate adapt flow before treating them as current evidence.
- Task-only: `define-tasks` / `refine-tasks` touch only tasks.md after product scope/package boundary is justified; do not alter prd.md, notes.md, validation.md, manifest.yaml, spec-catalog.yaml, or execution state.
- Technical-design: touch technical-design.md only, except bounded consistency fixes to notes.md or validation.md justified by the same planning evidence. Use for architecture, contracts, migration, observability, security, rollback, or option alignment. Do not create task decomposition, repo changes, execution steps, implementation notes, or validation evidence. If evidence is thin, write a small design with unknowns/open questions. Size: `small`, `medium`, `large`, or `unknown`. Verify facts through package evidence, repository code/tests/config/docs, or official dependency docs; unresolved claims go to `Open Questions`.
- Adapt: normalize pre-existing non-MAGO/drifted docs into the smallest truthful MAGO shape: full-package, product-only, tasks-only, or blocked partial. Then continue with `refine`, `refine-product`, or `refine-tasks`.
- Prepare-define: read define-queue.yaml, spec-catalog.yaml, and linked discovery evidence; seed only justified downstream artifacts; next mode is the queue entry's `define`, `define-product`, or `define-tasks`.

## Planning Boundary and Rules

MAGO plans/refines/documents; it does not implement product code or run execution workflows. Execution headings such as `Execution Rules`, task `Validation`, or `phase: execute` are artifact schema. New execution history belongs to MAGIA-owned `implementation-notes.md`; validation outcomes belong to `validation-evidence.md`. Reflect execution progress only when MAGIA evidence or repository truth supports it. If a request crosses into implementation, stop at planning.

Rules: preserve truthful history and discovery traceability; prefer bounded updates over rewrites; derive the smallest coherent artifact set current evidence supports; every changed artifact traces to repository truth, discovery evidence, or a necessary downstream clarification; record assumptions/risks/open questions in notes.md when in scope, otherwise in the touched artifact; do not ask for clarification during unattended loops; continue conservatively only when honest and downstream-enabling; block instead of inventing boundaries, dependencies, order, or status.

## Template Rules

Templates are structural references and script inputs first. Use `scripts/write_artifact_scaffold.py <artifact-path>` or narrower scripts for template-backed creation/refresh/normalization. After editing template-backed artifacts, run `scripts/validate_artifact.py <artifact-path>` or narrower validator. Replace placeholders/examples before completion. Preserve established values from catalog, package, discovery, or repository truth. Never blindly copy dynamic `cycle_version`, `order`, `spec_id`, `feature_key`, `feature_version`, `type`, `classification`, `status`, or `phase` from templates.

## Cross-Artifact Consistency

- Bootstrap a missing catalog with `cycle_version: 01.00.00` and `cycle_status: planned` unless repository truth says otherwise.
- Any `taskNNN` referenced by task `Dependencies`, `implementation-notes.md` execution-log subsections, or `manifest.yaml.last_execution.task_id` must exist in tasks.md.
- `implementation-notes.md` execution-log statuses: `not_started`, `in_progress`, `blocked`, `done`. Legacy notes.md execution logs are ignored until converted by MAGIA ADAPT.
- `manifest.yaml.last_execution`: required `task_id`; optional `date`, `summary`, `files_changed`; retain only current evidence-backed fields and do not invent noncanonical keys; omit when no task has truthfully executed.
- If task ids split or new ids appear, preserve old truthful history under old ids and let MAGIA add new execution-log subsections only for new ids during execution.

## Naming Rules

Directory names, file names, ids, YAML keys, and enums are lowercase. `board_id` and `cycle_version` must be safe POSIX path segments: no slashes, backslashes, empty segments, `.`, or `..` traversal.
