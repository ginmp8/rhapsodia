---
kind: mago-change-delta
authoritative: false
base_spec_id: "spec-2026-04-20-export"
target_spec_id: "spec-2026-04-20-export"
base_feature_version: "1.0.0"
target_feature_version: "1.1.0"
---
# Change Delta - Export
## Added Behavior
- REQ-002: Add ordered filtered columns.
## Modified Behavior
- none - Existing export trigger and authorization obligations are unchanged.
## Removed Behavior
- none - No behavior is removed.
## Preserved Behavior
- REQ-001: Preserve existing row filtering and authorization.
## Compatibility Impact
- Existing clients remain compatible; the new field is optional.
## Migration Impact
- none - No data or schema migration is required.
## Rollback Assumptions
- The optional request field can be ignored by reverting the consumer and service together.
## Merge and Retention
- Canonical merge target: prd.md, technical-design.md, tasks.md, validation.md
- Post-merge action: archive
- Source of truth after merge: Mago registry and canonical package artifacts
