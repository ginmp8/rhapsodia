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
| `order_hint` | optional presentation preference | yes |
| `depends_on_specs` | executable dependency constraint | yes |

Never use semantic versioning, counters, or list position as a filesystem identity.

## Atomic Identity Creation

Create identities only with `scripts/create_planning_identity.py`. It uses a date-readable slug plus a lowercase ULID and atomic exclusive file creation. Manual IDs are allowed only when importing proven repository truth during `adapt` and must still validate.

Two workers creating unrelated specs write different files:

```text
registry/spec-2026-07-19-audit-trail--<ulid-a>.yaml
registry/spec-2026-07-19-compliance-events--<ulid-b>.yaml
```

They do not modify a central list.

## Source of Truth

- `cycle.yaml` owns cycle identity and lifecycle metadata;
- each `registry/<spec_id>.yaml` owns one spec's registration, dependencies, handoff, and planning status;
- `specs/<spec_id>/manifest.yaml` mirrors immutable identity and package classification;
- package documents own detailed planning meaning;
- generated catalog/queue views are disposable projections.

Do not create source-controlled `spec-catalog.yaml` or `define-queue.yaml` under `BOARD_ROOT`. Render views to an external output directory when needed.

## Semantic Conflict Detection

The validator must reject:

- duplicate cycle or spec ULIDs across sibling cycles in the same board/year;
- multiple active cycles with the same `cycle_key` in the same board/year;
- an ID whose date/feature/ULID does not match metadata;
- multiple active specs with the same `feature_key` in one cycle unless supersession is explicit;
- missing dependencies or dependency cycles;
- package directories with no registry entry;
- registry/package manifest identity mismatches;
- shared catalog or queue files treated as canonical.

Duplicate active cycle or feature work is a real semantic conflict. Resolve it through merge, supersession, or an explicit dependency relationship; do not silently renumber it.

## Deterministic Views

`scripts/render_registry_views.py` builds catalog and define-queue projections from registry files. Ordering is deterministic:

1. dependency topology;
2. priority;
3. `order_hint`;
4. creation timestamp;
5. `spec_id` lexical tie-break.

The renderer includes a registry digest and must produce byte-identical output for the same inputs. Views are inspection/CI artifacts, not write targets.

## Old Planning Input

Old layouts may be read during `adapt`, but they never become an alternative active model. The result of adaptation is always the canonical structure described above.
