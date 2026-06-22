# Async Flow Analysis

Use this reference when a bug may appear after the initial request in SNS, SQS, Kafka, queues, topics, jobs, workers, workflows, or chained consumers.

## Causal map

Build a table:

| Step | Input event/command | Producer/consumer | Broker/topic/queue | State change | Side effect | Next event | Failure mode |
|---|---|---|---|---|---|---|---|

Always identify:

- event id, correlation id, causation id, tenant/resource ids, actor/origin, schema version, hop/depth when present;
- producers and consumers for each event;
- acknowledgement or offset commit timing;
- retry, backoff, visibility timeout, DLQ, poison message policy;
- redrive/replay/manual reprocessing path;
- terminal states and events forbidden after terminal state.

## Async-specific hypotheses

- duplicate event causes duplicate state or external side effect;
- consumer commits offset or deletes message before durable processing;
- consumer succeeds locally but fails before publishing next event;
- next event is published before local transaction commits;
- visibility timeout is shorter than processing time;
- retry policy creates storm, repeated calls, or DLQ too early/late;
- poison message blocks a partition or queue;
- event loop exists without hop limit, terminal condition, or deduplication;
- event arrives out of order or after terminal state and regresses state;
- schema old/new mismatch bypasses validation or breaks consumers;
- reprocessing from DLQ bypasses authorization, idempotency, or audit;
- subscriber receives data it should not receive.

## Broker checks

### SNS/SQS

- topic and queue policies restrict publishers/consumers;
- encryption at rest and in transit are enabled where required;
- DLQ redrive policy and max receive count are intentional;
- FIFO deduplication and message group keys match the business invariant;
- visibility timeout exceeds worst-case processing or is extended safely;
- sensitive payload retention and DLQ access are controlled.

### Kafka

- ACLs restrict produce/consume and consumer groups;
- keying/partitioning preserves required per-resource order;
- offset commit happens after safe processing;
- poison message strategy avoids permanent partition blockage;
- schema registry compatibility mode matches consumer expectations;
- replay permissions, retention, and compaction are intentional.

## Chain stabilization

A chain is ready for assertions when one of these is true:

- expected terminal event/state appears and no new event for the correlation id appears during the quiet window;
- all relevant queues/topics have no pending messages for the correlation id and no delayed retry remains;
- the configured timeout expires and the test reports incomplete chain evidence.

Use a quiet window that accounts for retry delays and broker visibility/commit behavior.

## Required async review output

- causal map or best-effort map;
- invariants and forbidden events;
- stress matrix for duplication, concurrency, out-of-order, replay, stale event, dependency failure, crash point, poison message, DLQ/redrive, and loop detection;
- evidence required to prove full-chain coverage;
- residual unknown consumers, topics, or side effects.
