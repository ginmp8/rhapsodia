# Dynamic Workflow Runtime Model

## At a Glance

- **Purpose:** Define the portable compile-to-workflow runtime model after a plan is accepted, including state ownership, resumption semantics, verification meaning, and runtime budgets.
- **Load when:** Compiling or executing an accepted adaptive plan, or deciding whether replay/resume, durability, verification isolation, or budget enforcement claims are valid.
- **Decision impact:** Keeps planner and runtime responsibilities separate, prevents session replay from being mislabeled durable execution, prevents isolation from being mislabeled independent truth, and requires runtime-enforced ceilings rather than prompt-only hints.

## Contents

- Resumption semantics
- Verification
- Budgets

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
