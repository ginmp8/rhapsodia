# dynamic-workflow-plan/v1

## At a Glance

- **Purpose:** Define the default contract for new runtime-adaptive orchestration plans, including authority, finite coverage, stage DAG semantics, hard runtime budgets, verification policy, termination, semantic capabilities, and evidence identities.
- **Load when:** Creating, reviewing, or validating a new `dynamic-workflow-plan/v1`, especially when work units or topology are discovered at runtime.
- **Decision impact:** Determines whether the plan is bounded and executable: authority remains fixed, coverage/DAG/budgets must be finite and valid, durable resume requires real durable state, deterministic-first verification is explicit, and no-progress/budget exhaustion terminates the run.
- **Do not load when:** Maintaining an existing `workflow-plan/v1`, validating historical `workflow-plan/v2`, or owning checkpoint promotion.

## Key Invariants

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
