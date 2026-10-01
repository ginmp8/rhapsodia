# Parallelization Map

## Purpose

Extend a repository context map with evidence needed to decide which work units may execute concurrently without changing ownership or correctness. This is planning evidence only; it never authorizes execution.

## Work-unit fields

For each material unit capture when relevant:

- `unit_id` and owning files/components;
- prerequisite unit ids;
- stable/shared immutable reads;
- freshness-sensitive reads;
- write set;
- external side effects;
- idempotency or reconcile-before-retry rule;
- validation output;
- isolation requirement;
- safe/unsafe parallel peers;
- evidence refs and confidence.

## Dependency rules

Create an ordering edge when:

- one unit consumes another's output;
- one unit reads state another mutates;
- write sets overlap;
- a migration/schema/public contract must land before a consumer;
- a generator/derived artifact creates ownership ordering;
- a global invariant or integration validation creates a barrier.

Unknown write overlap or dynamic consumers keep the pair serialized/provisional until evidence closes the gap.

## Safe patterns

- parallel read-only analysis over a frozen source snapshot;
- disjoint file/module changes with independent validation followed by one integration owner;
- isolated workspaces/worktrees with explicit merge ordering;
- pipeline execution when items share stage order but do not require global barriers.

## Risk flags

Flag at least:

- overlapping writes or write/read conflicts;
- generated-source ownership;
- shared database/schema migration;
- central dependency-registration/configuration files;
- public API/contract changes;
- non-idempotent external side effects;
- shared test fixtures/snapshots;
- cross-unit ordering hidden in runtime wiring.

## Output section

When execution topology is material, add an optional `Parallelization map` section to the context map:

```text
independent_units
ordered_edges
shared_reads
write_conflicts
safe_parallel_groups
unsafe_parallel_pairs
barriers
isolation_requirements
merge_owner
confidence/evidence_gaps
```

A downstream orchestrator may consume this evidence, but Context Architect remains owner only of repository evidence, ownership, dependency, and impact mapping.
