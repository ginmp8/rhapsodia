---
spec_id: spec-2026-07-20-filtered-export
feature_key: filtered-export
title: Filtered export
type: feature
classification: confidential
status: planned
phase: define
cycle_id: cycle-2026-07-20-q3-delivery
feature_version: 1.0.0
---

# PRD - Filtered export

## Context

Repository inspection shows the export endpoint currently emits every allowed field.

## Problem Statement

Authorized callers need a bounded field selection without exposing restricted columns.

## Goals

- Permit explicit allowed-column selection.
- Reject restricted and unknown columns deterministically.

## Non-Goals

- Changing export storage or retention.

## Current State

The endpoint has no caller-provided field selection.

## Proposed Outcome

The endpoint validates requested fields against a server-side allowlist.

## Functional Requirements

### REQ-001 - Select allowed columns

- Evidence basis: current export contract and repository handler inspection
- Failure/recovery behavior: invalid selections are rejected before export creation; callers may retry with an allowed set
- Verification: AC-001, AC-002

WHEN an authorized caller supplies allowed column identifiers, the export service MUST generate an export containing exactly those allowed columns.

### REQ-002 - Reject restricted columns

- Evidence basis: data-classification policy and current authorization boundary
- Failure/recovery behavior: restricted or unknown identifiers produce a safe validation error and no export artifact
- Verification: AC-002

IF a request contains a restricted or unknown column, THEN the export service MUST deny the request without logging customer values.

## Non-Functional Requirements

### NFR-001 - Validation latency

- Metric: p95 field-selection validation duration measured at the API boundary
- Threshold: at most 25 milliseconds for 100 requested identifiers
- Validation: VAL-003

## Constraints

- The existing export response contract remains backward compatible when no field list is supplied.

## Risks and Trade-Offs

- A stale allowlist can reject a newly approved field until configuration is updated.

## Acceptance Criteria

### AC-001 - Allowed selection succeeds

- Requirements: REQ-001
- Path: normal

```gherkin
Scenario: AC-001 allowed selection succeeds
  Given an authorized caller and an allowlist containing id and status
  When the caller requests id and status
  Then the export contains exactly id and status
```

### AC-002 - Restricted selection is denied

- Requirements: REQ-001, REQ-002
- Path: abuse

```gherkin
Scenario: AC-002 restricted selection is denied
  Given an authorized caller and a restricted field named tax_identifier
  When the caller requests id and tax_identifier
  Then the service rejects the request before creating an export
  And logs contain no customer values
```

## Open Questions

- None blocking.
