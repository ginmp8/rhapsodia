# Dynamic workflow runtime model

The portable model is **compile-to-workflow**:

`authorized objective -> planner/compiler -> accepted plan -> runtime -> isolated workers -> structured evidence -> verifier -> terminal decision`.

The planner chooses topology; it does not become the durable state store. Intermediate results, dependency state, retries, budgets, and execution trace belong to runtime/artifacts.

## Resumption semantics

- `none`: no replay/resume claim.
- `session-replay`: cached/session-scoped replay or resume. This is not durable workflow execution.
- `durable-external`: requires a real `durable-state` capability whose state/event history survives the planning context.

## Verification

Context isolation reduces contamination. It does not prove epistemic independence when producer and critic share the same model/model family. Prefer executable invariants, tests, deterministic graders, or external ground truth before model consensus.

## Budgets

Keep `max_parallel`, `max_workers`, `max_total_agents`, retries, and rounds separate. Planning hints are not runtime ceilings.
