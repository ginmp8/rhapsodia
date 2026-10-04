# Execution Lineage Profile

Use when a reproducibility or replay claim depends on a multi-stage/adaptive workflow. Traces show what happened; lineage additionally records which upstream identities each material result depends on and which outputs are canonical.

Validate `assets/schemas/execution-lineage.schema.json` with:

```text
<PYTHON> scripts/validate_reproducibility_profiles.py --kind lineage --input <LINEAGE.json>
```

Record planner/controller identity, accepted plan identity, evaluator identity, material nodes, dependencies, execution identity, input/output digests, replayability, invalidation keys, and canonical outputs. The validator checks dependency resolution, acyclicity, digest agreement, and emits a canonical lineage identity.

Changing the accepted plan, upstream canonical output, execution/tool/model identity, material invalidation key, or evaluator identity invalidates dependent evidence. If both plan and execution change, do not attribute the delta to only one layer.

This formal profile complements `references/workflow-execution-evidence.md`; use the lighter sidecar for descriptive orchestration evidence and this lineage profile when replay/invalidation correctness is part of the claim.
