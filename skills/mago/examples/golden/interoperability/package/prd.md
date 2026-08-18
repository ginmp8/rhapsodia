# PRD - Filtered export

## Functional Requirements

### REQ-001 - Preserve selected columns

WHEN a client requests an export with an allowed column selection, the export service MUST return exactly the selected columns in the requested stable order.

## Acceptance Criteria

### AC-001 - Selected columns are preserved

- Requirements: REQ-001

```gherkin
Scenario: AC-001 selected columns are preserved
  Given an allowed ordered column selection
  When the client requests an export
  Then the result contains exactly those columns in the same order
```
