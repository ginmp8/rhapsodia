# Distributed Debugging

## At a Glance

- **Purpose:** Localize failures across service/process/component boundaries without relying on timestamp guessing or one component's perspective.
- **Load when:** The failure crosses APIs, queues, workers, databases, CI stages, subprocesses, or other remote/process boundaries.
- **Decision impact:** Defines correlation evidence, boundary fields, retry/version/state checks, and security constraints for propagated diagnostic context.

## Contents

- Choose one execution
- Boundary evidence
- Correlation context
- Retry and partial-failure traps
- Cross-boundary security

## Choose one execution

Start with one failing request/workflow/message when possible. Preserve its correlation identity and timeline. Aggregated dashboards find patterns; one concrete execution usually localizes causality better.

## Boundary evidence

For each relevant boundary capture, when available:

- request/workflow/message identity;
- parent/child or causal relationship;
- input contract/version and relevant non-sensitive fields;
- output/result/error;
- attempt/retry number and idempotency key/state when applicable;
- duration/timeout/deadline;
- service/build/deploy/config identity;
- state transition before/after.

Compare what the sender says it sent with what the receiver says it received.

## Correlation context

Use an existing distributed tracing/correlation mechanism when available. Trace/span or equivalent request identities allow logs and spans from different components to be associated with the same execution. Do not invent a new correlation layer if the platform already has one.

## Retry and partial-failure traps

A successful retry can hide the original failure. Record each attempt separately. Check timeout/deadline propagation, duplicate delivery, partial commits, stale caches, eventual consistency, schema/version skew, and non-idempotent retry effects.

## Cross-boundary security

Treat propagated context as data crossing trust boundaries. Do not place credentials, API keys, PII, or customer payloads in diagnostic baggage/metadata. Sanitize or ignore untrusted incoming diagnostic context when the platform allows it, and avoid exposing internal identifiers to external services unless needed and approved.
