# Reachability and Reference Graph

## At a Glance

- **Purpose:** Define what counts as a reachability root, how typed references establish usage, and where static analysis stops proving consumer coverage.
- **Load when:** A resource appears unreferenced, runtime/build/packaging/external consumers may exist, or inventory/apply must reproduce the same root registry.
- **Decision impact:** Determines whether "unused" is supported by the evidence model, whether extra roots must be declared, and when a candidate must remain `unknown` or `integrable` instead of being removed.

Use this reference when deciding whether a resource is unused or when the default graph may miss a runtime, packaging, evaluator, or external consumer.

## Principle

Unused is always relative to known roots. A file that is not reachable from the recorded roots is not automatically dead; it is only unreachable under the current evidence model.

## Default roots

The inventory records these roots when present:

- `SKILL.md` as `skill-entrypoint`;
- files under `agents/` as `host-adapter-root`;
- files under `evals/` as `evaluator-root`;
- files under `tests/` as `test-root`.

Evaluator/test roots remain protected even when no production path reaches them.

## Declared roots

Add a root when a known consumer cannot be discovered safely from the package itself:

```text
<PYTHON> -S scripts/cleanup_inventory.py \
  --target <TARGET> \
  --root runtime-root:runtime/entry.json \
  --root packaging-root:packaging/manifest.json \
  --output <REPORT>/inventory.json
```

A declared root must be an existing canonical regular file inside the target. Missing or unsafe declared roots fail the inventory rather than silently reducing coverage.

When `cleanup_apply.py` must reproduce the same reachability decision, place the same roots in plan v2:

```json
{
  "plan_version": 2,
  "roots": [
    {"kind": "runtime-root", "path": "runtime/entry.json"}
  ],
  "actions": []
}
```

## Typed edges

`reference_edges` records how a local consumer reached a resource. Current deterministic kinds include:

- `markdown-link`;
- `markdown-image`;
- `markdown-reference`;
- `path-literal`;
- `python-import`;
- `javascript-import`.

`reference_graph` remains as a path-only adjacency map for backward compatibility. Use typed edges for review evidence and the adjacency graph for deterministic reachability.

## Coverage boundary

Static analysis cannot prove that no external or dynamic consumer exists. Before deletion, ask whether the package has:

- dynamic import/path construction;
- build-time generated consumers;
- external host/plugin manifests;
- public contracts consumed by another package;
- runtime configuration stored outside the target;
- documentation that names a non-static entrypoint.

If any material consumer is known but not represented, declare it as a root or keep the candidate `unknown`/`integrable`. Do not silence the gap with an ignore rule.

## Root identity in evidence

Every inventory report includes `root_registry`. Cleanup plans and reports should cite the exact registry used. If roots change after planning, re-run inventory and preflight; earlier reachability evidence is stale.
