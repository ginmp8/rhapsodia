# Execution Lineage Profile

## Purpose

Use this profile when a reproducibility claim depends on a multi-stage or adaptive workflow rather than one atomic action. Traces show what happened; lineage additionally records which upstream identities each material result depends on and which outputs are canonical.

Do not require a DAG manifest for simple single-stage work where a source/evaluator/artifact receipt already captures the full dependency relation.

## Contract

Use `assets/schemas/execution-lineage.schema.json` and validate with:

```text
<PYTHON> scripts/validate_execution_evidence.py --kind lineage --input <LINEAGE.json>
```

The validator checks unique nodes, dependency resolution, acyclicity, digest syntax, canonical-output references, and output-digest agreement. It emits a canonical lineage identity.

## Identity layers

Keep these identities distinct:

1. source/task identity when material;
2. planner/controller identity;
3. accepted workflow-plan identity;
4. per-node execution identities and output digests;
5. evaluator identity;
6. canonical output identities;
7. delivered artifact/receipt identity.

The lineage identity is not a substitute for any one of these; it binds the declared graph structure and observations into one evidence object.

## Node contract

Each material node records:

- stable node id and kind;
- upstream node ids;
- execution identity for the model/tool/human/transform attempt;
- material input digests;
- output digest;
- whether exact replay is supportable;
- an `invalidation_key` summarizing material configuration not already captured by upstream digests.

`replayable: true` means the workflow declares a supported replay path. It does not guarantee that an external API or stochastic model will return identical bytes.

## Invalidation and replay

Invalidate a node's prior evidence when any material dependency changes, including:

- accepted plan identity;
- upstream canonical output digest;
- execution/model/tool identity;
- material configuration represented by the invalidation key;
- evaluator identity when the result being reused is an evaluation decision.

Downstream evidence depending on an invalid node is invalid until recomputed or explicitly re-baselined. Reuse unaffected nodes only when their declared inputs and invalidation keys still match.

## Comparison rules

- Planner comparison: freeze source/task/evaluator inputs and compare accepted plan identities.
- Execution-repeatability comparison: freeze one accepted plan and compare multiple execution lineages/traces.
- If both plan and execution change, do not attribute the delta to one layer without an additional controlled arm.
- Record environment identity separately when runtime/provider/tool state can affect execution.

## Canonical outputs

`canonical_outputs` names the outputs that downstream acceptance or delivery actually depends on. Their digest must match the referenced node output. Intermediate logs/traces may be useful evidence without becoming canonical outputs.
