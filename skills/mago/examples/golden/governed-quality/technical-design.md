# Technical Design - Filtered export

## Context

The export API and worker share a canonical allowlist contract.

## Problem Statement

Field selection must be enforced before work is queued and rechecked by the worker.

## Scope

### In Scope

API validation, worker defense in depth, contract tests, metrics, and rollback.

### Out of Scope

Changing storage retention.

## Technical Solution

### Architecture Overview

The API normalizes requested fields, validates them against a versioned allowlist, and sends normalized identifiers to the worker. The worker revalidates before materializing data.

### Data Flow

Caller -> API validation -> queue -> worker validation -> export.

### Existing Reuse

Reuse the existing export authorization and queue contract.

### External Dependencies

No new external dependency.

### API and Data Contracts

The request adds an optional `fields` array. Omission preserves current behavior.

### Failure Modes

Invalid identifiers fail before queue publication; allowlist-version mismatch fails closed in the worker.

### Performance Requirements

Validation meets NFR-001.

### Migration Plan

Deploy consumers first because the new field is optional; then enable callers gradually.

## Alternatives Considered

### OPTION-001 - Validate only in the API

- Benefits: lowest implementation cost and latency
- Costs: worker trusts upstream input
- Failure modes: replayed or malformed queue messages can bypass current validation assumptions
- Operational impact: fewer metrics but weaker defense in depth

### OPTION-002 - Validate in API and worker

- Benefits: defense in depth and explicit rejection telemetry at both boundaries
- Costs: duplicate normalization logic must share a contract
- Failure modes: version drift between API and worker can temporarily reject valid requests
- Operational impact: adds an allowlist-version metric and alert

## Architecture Decisions

### DECISION-001 - Revalidate at both boundaries

- Requirements: REQ-001, REQ-002
- Selected option: OPTION-002
- Rationale: the queue is a trust boundary and restricted data exposure has high impact
- Consequences: API and worker must share versioned validation fixtures and emit version metrics

## Security Considerations

Restricted identifiers are denied and values are not logged.

## Testing Strategy

Contract, integration, negative, logging, and performance validation are required.

## Monitoring and Observability

Measure validation latency, rejection counts, and allowlist-version mismatches.

## Rollback Plan

Disable caller field selection while preserving the optional request field; revert worker enforcement only after queued messages are drained.

## Risks

Allowlist drift can cause safe false negatives.

## Execution Handoff Plan

Magia implements bounded API, contract, worker, test, and observability tasks.

## Open Questions

None blocking.
