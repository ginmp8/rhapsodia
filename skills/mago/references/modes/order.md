# Order Mode

## Purpose

Register bounded planning work without sequence counters or a shared mutable catalog. Each genuinely distinct capability receives one independent registry record.

## Canonical Rules

- Resolve one canonical `BOARD_ROOT` and valid `cycle.yaml`.
- No package path is writable in `order`.
- Write only `registry/<spec_id>.yaml` records.
- Generated catalog/queue files are external projections and never source of truth.

## Discovery Input Rules

Treat discovery artifacts as upstream evidence and traceability, not identity, version, dependency, status, or ordering truth. Never reuse a candidate ID as a spec ID.

## Workflow

1. Validate the cycle root.
2. Load `discovery-index.yaml`, selected candidate docs, relevant governance evidence, and existing registry records.
3. Deduplicate candidates by capability boundary and stable `feature_key`.
4. Preserve existing identity, dependencies, handoff, status, and supersession unless stronger evidence proves correction is necessary.
5. Create a new spec only for materially distinct work, using `scripts/create_planning_identity.py spec` for atomic identity/file creation.
6. Populate feature metadata, priority, optional `order_hint`, feature/spec dependencies, supersession, handoff status/mode/package shape, source candidates, seed artifacts, and blockers.
7. Use `type: fix` only for correction work; otherwise use the evidence-supported type/classification.
8. Validate duplicate active features, dependency existence/DAG, registry consistency, and cycle boundaries.
9. Render external catalog/queue views only when requested.

## Handoff Contract

- `handoff.status`: `ready_for_prepare_define`, `blocked`, or `needs_discovery`;
- `downstream_mode`: `define`, `define-product`, or `define-tasks`;
- `package_shape`: `full`, `product_only`, or `tasks_only`;
- source candidates resolve under the active cycle;
- seed artifacts match the selected package shape;
- blockers describe missing evidence/prerequisites, not merely the need for implementation.

Set `ready_for_prepare_define` only when evidence supports a stable package boundary and downstream shape. If evidence remains weak, keep `needs_discovery` or `blocked` rather than inventing readiness.

## Ordering and Conflict Rules

Dependencies constrain execution. `order_hint` is optional presentation metadata, may collide, and never defines identity. Broader enabling work may precede dependent slices. Duplicate active feature work is a semantic conflict resolved through reconciliation, supersession, or explicit dependency—not renumbering.

## Output

Order mode touches independent registry records only. It does not create package folders, implementation output, or source-controlled aggregate views. If existing records are already coherent, make only bounded evidence-backed corrections.
