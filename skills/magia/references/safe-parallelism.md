# Safe Execution Waves

Load only when a selected RALPH batch or explicit ADHOC work set may contain independent tasks. Parallelism is an execution optimization, never a reason to rewrite task dependencies, infer independence, or widen write scope.

## Default

Execute sequentially unless current evidence explicitly supplies:

- unique task ids;
- complete dependency edges;
- an explicit `parallel` or `independent` signal for every task proposed in the same wave;
- bounded write paths for every task;
- declared contract surfaces when APIs, events, schemas, files, permissions, or persisted data may be shared;
- isolated validation for each task and a final integration/reconciliation check.

Missing or uncertain information forces sequential execution or a Mago handoff; it never authorizes optimistic parallelism.

## Deterministic Analyzer

Use a temporary JSON input outside canonical planning artifacts:

```json
{
  "tasks": [
    {
      "id": "task001",
      "depends_on": [],
      "parallel": true,
      "write_paths": ["src/a.py"],
      "contract_surfaces": []
    }
  ]
}
```

Run:

```text
python scripts/analyze_execution_waves.py --input <tasks.json> --format json
```

The analyzer is read-only. It validates graph shape, detects cycles, builds topological layers, and serializes a layer when explicit permission, write scope, or contract isolation is missing. It does not execute tasks, edit `tasks.md`, or certify merge safety.

## Conflict Rules

Tasks must not run in the same wave when they:

- write the same path or ancestor/descendant paths;
- share a declared contract surface;
- depend directly or transitively on one another;
- have missing write scope;
- lack explicit parallel permission;
- require the same migration, lock, environment mutation, deployment gate, or non-isolated external resource;
- cannot be validated independently.

## Merge and Closure

For every parallel wave:

1. validate each task in isolation;
2. reconcile outputs and shared assumptions;
3. run the integration check for the combined state;
4. classify conflicts and failed checks honestly;
5. update controlled execution records only after the merged candidate passes applicable gates.

Parallel completion does not bypass dependency, evidence, traceability, security, compatibility, migration, rollback, or state-transaction requirements.
