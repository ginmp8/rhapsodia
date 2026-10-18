# Investigation Playbook

## At a Glance
- **Purpose:** Expand the six-step root workflow into concrete repository and flow traversal procedures.
- **Load when:** The flow crosses multiple files, workers, async boundaries, state stores, or a proposed change affects hidden callers.
- **Decision impact:** Determines which edges to inspect, when to stop, what distinguishes a possible call from an executable path, and how to prioritize verification.

## Entry and scope

Define an observable question, not a topic: e.g., "Can `Activated` be persisted when approval is absent?" Prefer one entry point, exit predicate and finite set of sources/revisions. Start from supplied evidence; if a repo is available, inspect real file content rather than naming guessed classes. Record workspace revision and relevant dirty/uncommitted state when available. A moving branch, injected config or runtime environment can invalidate an analysis.

Select the cheapest sufficiently powerful investigation: existing docs for vocabulary -> code symbols and usages -> implementation/control guards -> configuration/runtime wiring -> tests/trace evidence. A shallow search is a lead, not exhaustive evidence. Follow invocation sites as well as definitions; dynamic dispatch, DI registrations, reflection, routing, feature flags and generated bindings can invalidate naive static call graphs.

## Build a causal path ledger

For each material edge, record `source -> target`, trigger, guard, payload/input, state change/output, evidence locator, and status (`static-observed`, `runtime-observed`, `inferred`, `hypothesis`, `unknown`). Separate **control** (which branch), **data** (what information), **state** (before/after persistence) and **event** (publication/consumption). A symbol reference is not evidence of execution and a temporal correlation is not necessarily a causal edge.

Follow this order, pruning unrelated branches with the question boundary:

1. **Entrypoints:** HTTP route/middleware, CLI, UI, message/event handler, scheduled task, callback, internal call or manual operation.
2. **Guards:** authorization, validation, business invariant, conditional branch, feature flag, transaction boundary and environment override.
3. **Dispatch:** direct/static call, polymorphism, DI mapping, producer, queue/topic, consumer subscription, timer/job, external integration.
4. **State and effects:** read/write paths, repositories, caches, transaction/saga or outbox, audit, outbound notification; look for competing writers to the same state.
5. **Termination and failure:** successful exit, exception handling, retries, timeout, dead-letter, compensation, cancellation, rollback and abandoned work.
6. **Alternative routes:** other entrypoints and writers reaching the same exit/state; look in config, tests, migrations and runtime wiring when material.

Do not imply async delivery guarantees, ordering, exactly-once processing, idempotency, transactionality or cancellation semantics unless explicitly supported by code/config/runtime evidence. A durable message may be acknowledged before/after a commit; determine order rather than assume it.

## Reachability and change impact

For reachability, define origin/state, target line/state and constraints. Distinguish *syntactically possible* routes from routes feasible under guards/config and the actual observed execution. Use an enumerated path list if scope is finite. A static call graph can overapproximate feasible behavior; a trace samples, rather than exhausts, execution.

For proposed-change impact: start with the changed symbol/contract/schema, find upstream consumers and downstream effects, and explicitly inspect serialization, dispatch, persistence, observability and test fixtures as relevant. Report potential impact with evidence and uncertainty. Do not implement, approve deployment or silently widen the change.

## Investigation budget / stopping

Start with the smallest meaningful boundary. Prioritize: paths that reach the requested outcome; external side effects/state mutation; branches with altered guards; asynchronous ambiguity; other writers; finally incidental helper details. Stop on a supported scoped conclusion, or when evidence cost outweighs remaining decision impact. Preserve named unknowns rather than inventing exhaustive completeness.

## Explain so understanding can be tested

Use a short mechanism narrative with a branch/state table or diagram only when it reduces cognitive load. Then ask: "What input/configuration makes this explanation false?", "What competing route reaches the same state?", and "What would I observe if this model were wrong?" A successful explanation predicts what happens under at least one changed condition. Avoid an attractive diagram whose arrows lack source provenance.
