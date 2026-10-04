# Concurrency and Distributed Oracles

A stable final state is not always sufficient evidence for a concurrency or consistency claim.

## Select the claimed correctness model first

Examples include:

- single durable side effect under duplicate delivery;
- linearizable operation history;
- serializable or snapshot-isolated transaction history;
- at-least-once handling with idempotent externally visible effects;
- retry safety after partial failure;
- absence of a forbidden interleaving or race.

Do not strengthen the claim beyond the source requirement.

## Observation design

When the claim depends on operation ordering/history, capture enough history to run the relevant checker or reconstruct the violation. Record, as applicable:

- consistency/correctness model;
- operation invocation/completion and identities;
- history capture format;
- checker/evaluator identity;
- systematic or recorded scheduler policy;
- fault-injection policy;
- minimal counterexample/history on rejection.

Use systematic schedule exploration when feasible for bounded concurrent components. Use history-based consistency checking for distributed/database claims when final-state assertions would miss invalid histories.

A stress loop without a frozen schedule/history model is supporting evidence, not automatically a strong oracle.
