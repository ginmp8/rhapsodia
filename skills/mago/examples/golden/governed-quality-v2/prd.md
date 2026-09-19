---
quality_contract: 2
---
# PRD - Governed Quality V2

## Functional Requirements

### REQ-001 - Resumable export
- Evidence basis: Incident INC-42 and repository export worker inspection.
- Failure/recovery behavior: Failed chunks remain idempotently retryable without duplicating completed output.
- Verification: AC-001, AC-002, AC-003
- Criticality: high
- Criticality basis: Partial or duplicate financial exports create material reconciliation risk.

WHEN an authorized export is requested, the export service MUST produce each selected row exactly once.

## Non-Functional Requirements

### NFR-001 - Recovery time
- Metric: Recovery completion time after a worker restart.
- Threshold: 95 percent of interrupted exports resume within 60 seconds.
- Validation: VAL-003

## Acceptance Criteria

### AC-001 - Normal completion
- Requirements: REQ-001
- Path: normal
```gherkin
Scenario: AC-001 Normal completion
  Given an authorized export with valid selected columns
  When the export completes
  Then every selected row appears exactly once
```

### AC-002 - Worker interruption recovery
- Requirements: REQ-001
- Path: recovery
```gherkin
Scenario: AC-002 Worker interruption recovery
  Given a partially completed export with a persisted checkpoint
  When a replacement worker resumes the export
  Then completed chunks are not duplicated
```

### AC-003 - Invalid checkpoint rejection
- Requirements: REQ-001
- Path: error
```gherkin
Scenario: AC-003 Invalid checkpoint rejection
  Given a checkpoint that does not match the export identity
  When a worker attempts to resume
  Then the worker rejects the checkpoint and records a safe diagnostic
```
