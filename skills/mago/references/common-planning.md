# Common Planning

## Canonical Model

- `board_id`: stable board segment;
- `year`: creation-year path segment;
- `cycle_id`: immutable date + cycle key + ULID identity;
- `spec_id`: immutable date + feature key + ULID identity;
- `feature_key`: stable lowercase kebab-case functional identity;
- `feature_version`: semantic capability/fix version;
- `proposed_version` / `accepted_version`: optional delivery metadata, never path identity.

## Layout

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
    implementation-notes.md       # MAGIA-owned when execution exists
    validation-evidence.md        # MAGIA-owned when validation exists
```

Generated views belong outside `BOARD_ROOT`, for example `<output>/spec-catalog.yaml` and `<output>/define-queue.yaml`.

## Source of Truth

- `cycle.yaml`: cycle identity, status, proposed/accepted version, planning revision;
- `registry/<spec_id>.yaml`: spec registration, dependencies, status, priority, order hint, and define handoff;
- `manifest.yaml`: package identity, classification, planning phase, source-of-truth and traceability maps;
- detailed package documents: planning meaning;
- MAGIA-owned execution artifacts: runtime/execution evidence only.

## Dependencies and Status

- `depends_on_features`: stable feature keys;
- `depends_on_specs`: immutable spec IDs;
- task `Dependencies`: task-local `taskNNN` prerequisites;
- cycle status: `proposed`, `planned`, `in_progress`, `done`, `cancelled`;
- spec status: `planned`, `in_progress`, `blocked`, `done`, `cancelled`, `superseded`;
- manifest phase: `define`, `execute`, `review`, `done`.

`order_hint` is not unique and never determines identity. Dependency topology is authoritative for executable ordering.

## Mode Boundaries

- `order`: create or reconcile independent registry records; do not create package folders.
- `prepare-define`: read one registry record and seed only justified package artifacts.
- `define` / `refine`: work on exactly one package unless explicitly bounded otherwise.
- product-only modes do not alter tasks or execution state.
- task-only modes do not alter product docs, registry identity, or execution state.
- technical-design mode touches technical design and only bounded consistency corrections justified by the same evidence.
- `adapt`: translate old-layout planning input into the canonical model or repair demonstrable canonical drift; preserve source traceability without keeping a parallel active model.

## Planning Boundary

MAGO plans and documents. It does not implement product code or claim runtime evidence. Execution-required tasks are valid planning outputs when bounded, evidence-backed, and explicitly handed to MAGIA with a credible validation path.

Preserve truthful history; prefer bounded changes; record assumptions, risks, and open questions; block rather than invent boundaries, dependencies, status, or evidence.

## Template Rules

Use `scripts/create_planning_identity.py` for cycle/spec identity and registry creation. Use `scripts/write_artifact_scaffold.py` for template-backed package artifacts. Replace all dynamic values with repository truth or explicit unresolved values allowed by the artifact contract. Never copy example IDs, dates, versions, statuses, or dependencies into completed artifacts.

## Cross-Artifact Consistency

- `cycle.yaml.cycle_id` must match the cycle directory;
- registry filename and `spec_id` must match;
- registry `cycle_id` must match `cycle.yaml`;
- package directory, registry `spec_id`, and manifest `spec_id` must match;
- manifest `cycle_id` must match the active cycle;
- active `feature_key` values must be unique within a cycle unless supersession is explicit;
- all spec dependencies must resolve and form an acyclic graph;
- any task referenced by dependencies or execution evidence must exist in tasks.md;
- execution status/completion changes require MAGIA or repository evidence.

## Naming Rules

Directory names, filenames, IDs, YAML keys, and enums are lowercase. Slugs use lowercase kebab-case. Dynamic path segments must not contain slashes, backslashes, traversal, whitespace padding, or unresolved tokens.
