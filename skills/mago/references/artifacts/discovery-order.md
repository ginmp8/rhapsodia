# Discovery and Order Artifacts

## Discovery State

Discovery artifacts live under the canonical cycle root:

```text
discovery-state.json
discovery-index.yaml
candidates/<candidate_id>.md
```

They capture repository frontier, processed paths, candidate evidence, confidence, traceability, blockers, and open questions. They do not own cycle/spec IDs, feature versions, dependencies, order, handoff readiness, or execution status.

Discovery must preserve source paths, distinguish observed facts from inference, and continue in bounded batches. Weak or contradictory evidence remains blocked rather than being promoted into registration.

## Order Source of Truth

Each ordered item is an independent file:

```text
registry/<spec_id>.yaml
```

Create new identities atomically through `scripts/create_planning_identity.py spec`. Reconcile an existing record only when immutable identity remains unchanged and evidence supports the update.

Required registry areas:

- immutable spec/cycle identity and creation metadata;
- feature key/version, title, type, classification;
- lifecycle status, priority, optional `order_hint`;
- feature and spec dependencies;
- supersession links;
- handoff status, downstream mode, package shape, source candidates, seed artifacts, blockers;
- optional import traceability.

Every source candidate resolves under the active cycle root. Every spec dependency resolves to another registry record. Active duplicate feature keys and dependency cycles are invalid.

## Ordering and Deduplication

- Deduplicate by capability boundary and stable `feature_key` before creating an identity.
- Dependencies constrain execution; `order_hint` is only presentation metadata and may collide.
- Preserve existing registry identity and dependencies unless stronger evidence proves correction is necessary.
- Broader enabling work may precede dependent slices, but do not force weak evidence into the registry.
- `handoff.status: ready_for_prepare_define` requires enough evidence to justify downstream mode and package shape.

## Generated Views

`scripts/render_registry_views.py` emits external inspection/CI projections:

- `spec-catalog.yaml`;
- `define-queue.yaml`.

The templates document their complete output schemas. The renderer output includes a registry digest and must be deterministic. Generated views never become canonical board files, hand-edit targets, or execution-state synchronization surfaces.
