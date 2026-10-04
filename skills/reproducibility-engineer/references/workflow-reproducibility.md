# Workflow Reproducibility

## Purpose

Separate variability introduced by planning/orchestration from variability introduced by workers executing an accepted plan.

## Identity model

For material adaptive workflows keep, when available:

1. `source_identity` - evidence/task inputs used by planning;
2. `planner_identity` - controller/instructions/model configuration that generated or selected the plan;
3. `workflow_plan_identity` - normalized accepted plan;
4. `execution_trace_identity` - one observed execution of that plan;
5. `evaluator_identity` - independent acceptance criteria/evaluator.

Never collapse planner, plan, trace, and evaluator identity into one generic run id. When dependency identity matters across multiple stages, persist the graph using `references/execution-lineage.md`; a text trace alone does not prove which upstream bytes/configuration a canonical output depends on.

## Variability classes

### Planning variance

Symptoms: different decomposition, worker count, strategy, dependency graph, verification layout, or budgets for materially equivalent input.

Controls: bounded strategy set, normalized plan contract, deterministic tie-breakers where appropriate, explicit budget/default policy, plan validator, frozen plan before measured execution.

### Execution variance

Symptoms: same plan but different worker findings, ordering, tool results, or synthesis.

Controls: stable inputs, isolated/fresh contexts where required, fixed evaluator, trace capture, repeated runs when variability matters, deterministic mechanics around parsing/aggregation.

### External runtime variance

Symptoms: host capability differences, concurrency scheduling, mutable repositories, changing web/API state.

Controls: capability profile, source snapshot, validated environment/version identity from `references/environment-provenance.md` when material, explicit degradation, state reconciliation before retries.

## Persistent execution lineage

For a material multi-stage workflow, use `assets/schemas/execution-lineage.schema.json` and validate the captured graph with:

```text
<PYTHON> scripts/validate_execution_evidence.py --kind lineage --input <LINEAGE.json>
```

Each node should bind its upstream node ids, execution identity, material input digests, output digest, replayability declaration, and invalidation key. Canonical outputs must resolve to node outputs. A changed upstream digest or invalidation key invalidates dependent evidence until recomputed or explicitly re-baselined.

## Comparison rules

- To evaluate planner quality, freeze task/source/evaluator inputs and compare plan identities.
- To evaluate execution repeatability, freeze one accepted plan and compare multiple traces/lineages under materially comparable environment identities.
- If both plan and execution change, do not attribute a delta to either layer without additional evidence.
- A host-specific runtime may improve throughput without changing semantic plan quality; report runtime evidence separately.

## Fresh-context verification

When independence is part of the claim, record whether the verifier received a fresh context and whether evaluator-only data or producer hidden reasoning was exposed. Independence is an evidence property, not a prompt label.
