# Concurrent Planning Model

## Design Goal

Allow unrelated developers or agents to create planning work in parallel without coordinating a sequence number or editing a shared catalog. Preserve real semantic conflicts instead of hiding them.

## Identity, Version, and Order

| Field | Meaning | Mutable |
|---|---|---|
| `cycle_id` | physical identity of one planning cycle | no |
| `spec_id` | physical identity of one planning item | no |
| `feature_key` | stable functional identity | only by explicit correction |
| `feature_version` | semantic evolution of a capability | yes |
| `proposed_version` | intended delivery version | yes |
| `accepted_version` | approved delivery version | only with evidence |
| `business_priority` | read-only Nomia business urgency/importance with provenance | only by refreshed Nomia evidence |
| `technical_criticality` | technical risk and blast-radius classification | yes, with rationale |
| `execution_sequence` | dependency-safe lane, optional rank, and rationale | yes |
| `depends_on_specs` | executable dependency constraint | yes |

Never use semantic versioning, counters, or list position as a filesystem identity.

## Atomic Identity Creation

Create identities only with `scripts/create_planning_identity.py`. It uses the canonical date-readable cycle/spec format and atomic exclusive file creation. Manual canonical IDs are allowed only when importing proven repository truth during `adapt` and must still validate.

Two workers creating unrelated specs write different files:

```text
registry/spec-2026-07-19-audit-trail.yaml
registry/spec-2026-07-19-compliance-events.yaml
```

They do not modify a central list. Distinct specs require distinct `feature_key` values. If a canonical ID or path already exists, do not overwrite it, add a suffix, or increment shared state. Reuse is allowed only after the existing record is proven identical; otherwise report an identity collision.

## Source of Truth

- `cycle.yaml` owns cycle identity and lifecycle metadata;
- each `registry/<spec_id>.yaml` owns one spec's registration, dependencies, handoff, and planning status;
- `specs/<spec_id>/manifest.yaml` mirrors immutable identity and package classification;
- package documents own detailed planning meaning;
- generated catalog/queue views are disposable projections.

Do not create source-controlled `spec-catalog.yaml` or `define-queue.yaml` under `BOARD_ROOT`. Render views to an external output directory when needed.

## Semantic Conflict Detection

The validator must reject:

- multiple active cycles with the same `cycle_key` in the same board/year;
- an ID whose date, cycle key, or feature key does not match metadata;
- a canonical ID/path collision that represents a different record;
- multiple specs with the same `feature_key` in one cycle;
- missing dependencies or dependency cycles;
- package directories with no registry entry;
- registry/package manifest identity mismatches;
- shared catalog or queue files treated as canonical.

Duplicate active cycle or feature work is a real semantic conflict. Resolve it through merge, supersession, or an explicit dependency relationship; do not silently renumber it.

## Deterministic Views

`scripts/render_registry_views.py` builds catalog and define-queue projections from registry files. Ordering is deterministic:

1. dependency topology and safety constraints;
2. `execution_sequence.lane`;
3. `execution_sequence.rank`;
4. creation timestamp;
5. `spec_id` lexical tie-break.

`business_priority` never participates directly in sorting. `technical_criticality` never implies order. Any non-default lane or explicit rank requires rationale.

The renderer includes a registry digest and must produce byte-identical output for the same inputs. Views are inspection/CI artifacts, not write targets.

## Old Planning Input

Old layouts and IDs with ULID suffixes may be read only during `adapt`, but they never become valid canonical identities or an alternative active model. Preserve a legacy ID only as read-only traceability metadata. The result of adaptation is always the canonical structure described above.
