# dynamic-workflow-plan/v1

Use for new runtime-adaptive workflows. The contract separates objective/authority, coverage, stage DAG, runtime semantics, hard budgets, verification policy, termination, semantic capabilities, and evidence identities.

Key invariants:

- topology remains inside one already-authorized lifecycle phase;
- runtime-discovered coverage is finite through `coverage.max_items`;
- dependency graph is acyclic;
- read-only stages do not write;
- hard ceilings satisfy `max_parallel <= max_workers <= max_total_agents`;
- durable execution requires a bound `durable-state` capability;
- deterministic-first verification is explicit;
- `same_model_independence_claim` is always false;
- no-progress and budget exhaustion terminate rather than silently expanding work.

Historical `workflow-plan/v1` and `workflow-plan/v2` remain compatibility contracts and are not silently rewritten.
