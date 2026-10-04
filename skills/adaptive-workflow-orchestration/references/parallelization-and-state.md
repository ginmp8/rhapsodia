# Parallelization and State

## Safe concurrency test

Before two stages can be runnable together, prove all of the following:

1. no dependency path orders them;
2. their authority is already valid independently;
3. read/write resources are known enough to check conflicts;
4. no write/write or read/write overlap exists;
5. external side effects are absent or separately coordinated;
6. each result can be attributed to a stable work unit;
7. the orchestrator owns integration/synthesis.

If any item is unknown, serialize or block.

## Resource sets

Use resource ids/paths that are stable enough for comparison. Prefer canonical repository paths, contract ids, dataset ids, or explicit named state over vague prose such as `the config`.

A write to a generated artifact should normally be modeled against the owning source/generator too, not only the generated file.

## State ownership

The orchestrator owns:

- stage status;
- dependency satisfaction;
- retry/re-entry counters;
- cancellation/stop-new-dispatch state;
- plan identity;
- terminal state;
- synthesis/merge decision.

Workers own only their bounded result/evidence. They do not directly mark the overall workflow completed.

## Failure and partial results

Define how sibling results are treated when one unit fails:

- `stop`: stop new dispatch and terminate/repair according to policy;
- `continue-independent`: keep unaffected units but do not synthesize a required missing unit as if complete;
- `retry`: reconcile state first, then use the finite retry budget;
- `repair`: return to one explicit repair owner;
- `escalate`: terminate autonomous progression.

## Cancellation

When a hard blocker, exhausted budget, revoked authority, or invalidated source identity is observed:

1. stop dispatching new units;
2. cancel pending work when the host supports safe cancellation;
3. preserve completed evidence with its original identity;
4. mark uncertain side effects explicitly;
5. reconcile before any retry/resume.

## Fresh-context convergence

Long-horizon repair loops should prefer fresh contexts that reload:

- current candidate/source state;
- the bounded reference slice;
- frozen oracle/rubric identity;
- latest accepted feedback;
- remaining budgets and stop conditions.

Do not use a growing transcript as the primary state store. Source artifacts and evidence records are authoritative.

Independent checkpoints may converge in parallel only when their write sets and authoritative state are isolated. Shared canonical writers remain serialized.
