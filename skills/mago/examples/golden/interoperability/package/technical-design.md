---
spec_id: "spec-2026-07-20-filtered-export"
cycle_id: "cycle-2026-07-20-governed-review"
feature_key: "filtered-export"
title: "Filtered export"
type: "feature"
classification: "internal"
status: "planned"
phase: "define"
feature_version: "0.1.0"
project_size: "medium"
project_types:
  - public_contract
  - production_change
depends_on_features: []
depends_on_specs: []
---

# Technical Design - Filtered export

## Context

The existing export pipeline accepts an ordered set of allowed columns and already preserves projection order after request validation.

## Problem Statement

The plan must reject disallowed selections while preserving the exact allowed order without introducing a second ordering model.

## Scope

This decision covers request-boundary validation and the projection contract for filtered exports. Storage layout and unrelated export formats are excluded.

## Technical Solution

Validate the ordered selection at the request boundary, pass the validated ordered list to the existing projection path, and preserve the current single source of ordering truth.

## Architecture Decisions

### DECISION-001 - Validate and preserve ordered selection

- Requirements: REQ-001
- Status: accepted
- Rationale: The existing export pipeline already preserves projection order, so validation at the request boundary avoids a second ordering model.

## Security Considerations

Only allowlisted columns may cross the request boundary. Authorization and data-classification rules remain unchanged and must be revalidated by downstream contract tests.

## Testing Strategy

Magia must execute the contract test described by VAL-001, including allowed order, rejected columns, duplicate input, and empty-selection behavior.

## Monitoring and Observability

Reuse current export failure metrics and add a validation-rejection reason only when the repository already supports structured rejection categories.

## Rollback Plan

Revert the request-boundary validation change and restore the prior projection call while preserving the canonical specification and recorded deviation evidence.

## Risks

A consumer may rely on undocumented column normalization. Contract validation must identify such compatibility assumptions before rollout.

## Execution Handoff Plan

Implement the bounded request-validation change, update the existing contract tests, and return runtime evidence through Magia-owned validation artifacts.

## Open Questions

Confirm whether duplicate selected columns are rejected or de-duplicated by the current public contract before implementation begins.
