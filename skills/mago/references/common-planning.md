# Common Planning

## Canonical Model

- `board_id`: required stable repository board segment under `docs/boards/`.
- `year`: creation-year path segment; it must match the date encoded in `cycle_id`.
- `cycle_id`: immutable physical cycle identity in `<yyyy-mm-dd>-<cycle-key>--<ulid>` format.
- `spec_id`: immutable physical spec identity in `spec-<yyyy-mm-dd>-<feature-key>--<ulid>` format; preserve once assigned unless repository truth proves identity corruption.
- `feature_key`: stable lowercase kebab-case functional identity; it remains separate from physical `spec_id`.
- `feature_version`: semantic capability/fix version; never use semantic versioning for filesystem identity or roadmap order.
- `proposed_version` / `accepted_version`: optional delivery metadata; they do not define directories or IDs.
- `order_hint`: optional presentation preference; it is not unique and does not define identity.

## Operational Roots and Layout

Load defaults from `references/canonical-paths.md`. `BOARD_ROOT` is the active boundary; use a prompt-provided root when valid, otherwise derive it from concrete `board_id`, `year`, and `cycle_id`. Package paths derive from `BOARD_ROOT/specs/<spec_id>/`. Registry paths derive from `BOARD_ROOT/registry/<spec_id>.yaml`. Do not create parallel aliases.

```text
BOARD_ROOT/
  cycle.yaml
  discovery-state.json
  discovery-index.yaml
  candidates/<candidate_id>.md
  registry/<spec_id>.yaml
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

Generated inspection/CI projections belong outside `BOARD_ROOT`, for example `<output>/spec-catalog.yaml` and `<output>/define-queue.yaml`. They are recreated from registry records and never become canonical write targets.

Block if required root segments cannot be proven. All modes write under `BOARD_ROOT`. Full packages normally use the package layout; technical-design.md is optional and used only for material architecture/contract alignment. Spec-local auxiliary docs may clarify downstream execution but must not replace canonical files. Product-only modes touch prd.md, notes.md, optional validation.md. Task-only modes touch tasks.md only. Discovery uses discovery-state.json, discovery-index.yaml, and `candidates/`. Root cycle folders outside the canonical year/cycles layout, ad hoc `docs/mago/`, legacy version folders, and docs outside `BOARD_ROOT` are noncanonical active writes.

## Source of Truth

- `BOARD_ROOT`: mandatory location boundary.
- `cycle.yaml`: cycle identity, lifecycle status, proposed/accepted delivery metadata, planning revision, import traceability.
- `registry/<spec_id>.yaml`: one spec registration, feature identity, dependencies, status, priority, order hint, supersession, define handoff, and source candidates.
- generated `spec-catalog.yaml`: deterministic catalog projection for inspection only; never the source of truth.
- generated `define-queue.yaml`: deterministic define-handoff projection for inspection only; never the source of truth.
- manifest.yaml: package identity, classification, planning `status`/`phase`, `source_of_truth`, traceability, optional truthful `last_execution` preserved from MAGIA evidence.
- prd.md, technical-design.md, notes.md, validation.md, tasks.md when present: detailed planning meaning. `implementation-notes.md` and `validation-evidence.md` are MAGIA-owned execution evidence when present.
- technical-design.md: optional selected-spec architecture/data-flow/contract/security/monitoring/rollback/implementation-approach alignment.
- tasks.md plus execution-labeled fields: downstream execution contract, not MAGO execution authority.

## Dependencies and Status

- Dependencies: `depends_on_features` = `feature_key` list; `depends_on_specs` = immutable `spec_id` list; task `Dependencies` = task-local prerequisites.
- Cycle status: `proposed`, `planned`, `in_progress`, `done`, `cancelled`.
- Spec status: `planned`, `in_progress`, `blocked`, `done`, `cancelled`, `superseded`.
- Manifest `phase`: `define`, `execute`, `review`, `done`.
- Dependency topology is authoritative for executable ordering. Priority and `order_hint` are secondary deterministic presentation inputs.

## Mode Boundaries

- Product-only: `define-product` / `refine-product` touch only prd.md, notes.md, optional validation.md; do not alter tasks.md, registry identity/dependencies, generated order, or execution state. Product-only notes omit execution records. If legacy execution sections are present, run the appropriate adapt flow before treating them as current evidence.
- Task-only: `define-tasks` / `refine-tasks` touch only tasks.md after product scope/package boundary is justified; do not alter prd.md, notes.md, validation.md, manifest.yaml, registry identity, generated views, or execution state.
- Technical-design: touch technical-design.md only, except bounded consistency fixes to notes.md or validation.md justified by the same planning evidence. Use for architecture, contracts, migration, observability, security, rollback, or option alignment. Do not create task decomposition, repo changes, execution steps, implementation notes, or validation evidence. If evidence is thin, write a small design with unknowns/open questions. Size: `small`, `medium`, `large`, or `unknown`. Verify facts through package evidence, repository code/tests/config/docs, or official dependency docs; unresolved claims go to `Open Questions`.
- Adapt: translate old-layout planning input into the smallest truthful canonical shape: full-package, product-only, tasks-only, or blocked partial. Preserve original identifiers and paths only as import traceability. Then continue with `refine`, `refine-product`, or `refine-tasks`.
- Order: create or reconcile independent registry records. Do not create package directories or hand-edit shared aggregate files.
- Prepare-define: read one registry handoff plus linked discovery evidence; seed only justified downstream artifacts; next mode is the registry handoff's `define`, `define-product`, or `define-tasks`.

## Planning Boundary and Rules

MAGO plans/refines/documents; it does not implement product code or run execution workflows. Execution headings such as `Execution Rules`, task `Validation`, or `phase: execute` are artifact schema. New execution history belongs to MAGIA-owned `implementation-notes.md`; validation outcomes belong to `validation-evidence.md`. Reflect execution progress only when MAGIA evidence or repository truth supports it. If a request crosses into implementation, stop at planning.

Rules: preserve truthful history and discovery traceability; prefer bounded updates over rewrites; derive the smallest coherent artifact set current evidence supports; every changed artifact traces to repository truth, discovery evidence, or a necessary downstream clarification; record assumptions/risks/open questions in notes.md when in scope, otherwise in the touched artifact; do not ask for clarification during unattended loops; continue conservatively only when honest and downstream-enabling; block instead of inventing boundaries, dependencies, priority, order, handoff readiness, or status.

## Template Rules

Templates are structural references and script inputs first. Use `scripts/create_planning_identity.py` for cycle/spec identity and registry creation. Use `scripts/write_artifact_scaffold.py <artifact-path>` or narrower scripts for template-backed creation/refresh/normalization. After editing template-backed artifacts, run `scripts/validate_artifact.py <artifact-path>` or a narrower validator. Replace placeholders/examples before completion. Preserve established values from cycle metadata, registry, package, discovery, or repository truth. Never blindly copy dynamic `year`, `cycle_id`, `spec_id`, `feature_key`, `feature_version`, `type`, `classification`, `status`, `phase`, dependencies, or handoff values from templates.

## Cross-Artifact Consistency

- `cycle.yaml.cycle_id` must match the cycle directory and its date/year metadata.
- registry filename, registry `spec_id`, and package directory must match.
- registry `cycle_id` must match cycle.yaml.
- manifest identity fields must match registry identity and the active cycle.
- active `feature_key` values must be unique within a cycle unless explicit supersession makes the relationship unambiguous.
- all `depends_on_specs` must resolve and form an acyclic graph; feature dependencies must be consistent with registered capabilities when resolvable.
- any `taskNNN` referenced by task `Dependencies`, implementation-notes.md execution-log subsections, or `manifest.yaml.last_execution.task_id` must exist in tasks.md.
- `implementation-notes.md` execution-log statuses: `not_started`, `in_progress`, `blocked`, `done`. Legacy notes.md execution logs are ignored until converted by MAGIA ADAPT.
- `manifest.yaml.last_execution`: required `task_id`; optional `date`, `summary`, `files_changed`; retain only current evidence-backed fields and do not invent noncanonical keys; omit when no task has truthfully executed.
- if task ids split or new ids appear, preserve old truthful history under old ids and let MAGIA add new execution-log subsections only for new ids during execution.
- generated catalog/queue projections must be byte-stable for the same registry content and must never be edited back into canonical state.

## Naming Rules

Directory names, file names, ids, YAML keys, and enums are lowercase. Slugs use lowercase kebab-case. `board_id`, `year`, `cycle_id`, and `spec_id` must be safe POSIX path segments: no slashes, backslashes, empty segments, `.`, `..` traversal, whitespace padding, or unresolved tokens.
