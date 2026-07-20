# Technical Design - Filtered export

## Architecture Decisions

### DECISION-001 - Validate and preserve ordered selection

- Requirements: REQ-001
- Status: accepted
- Rationale: The existing export pipeline already preserves projection order, so validation at the request boundary avoids a second ordering model.
