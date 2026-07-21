# Execution Wave Projection

Use a dependency-wave projection when the canonical task plan is complete enough for Magia to consider safe sequencing. The projection is generated, disposable, and never executes tasks.

## Command

```bash
python -B scripts/render_execution_waves.py <package>/tasks.md --output <external-path>.json
python -B scripts/render_execution_waves.py <package>/tasks.md --format markdown --output <external-path>.md
```

## Deterministic rules

- Parse stable `taskNNN` records and their `Dependencies` fields.
- Reject duplicate IDs, unknown dependencies, self-dependencies, unresolved placeholders, and cycles.
- Place tasks with no unresolved predecessors in the same wave.
- Preserve source order inside each wave.
- Calculate a dependency critical path for planning visibility.
- Mark integration, validation, migration, rollout, and hardening tasks as coordination gates when their task type indicates that role.

## Safety boundary

A wave means dependency-safe according to the canonical task text only. It does not prove that tasks are safe to execute concurrently. Magia must still inspect:

- overlapping files or modules;
- shared contracts, schemas, migrations, feature flags, or infrastructure;
- common test fixtures and mutable environments;
- runtime ordering and rollout constraints;
- newly discovered implementation dependencies.

If overlap or new evidence contradicts the projection, Magia must serialize execution and report the planning deviation to Mago. Mago may then refine dependencies; it must not execute the tasks.
