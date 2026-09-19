# Validation - Governed Quality V2

### VAL-001 - Normal export
- Requirements: REQ-001
- Acceptance: AC-001
- Tasks: task001
- Environment: Isolated integration environment with deterministic export fixture.
- Command or procedure: Run the export integration scenario with a fixed 100-row fixture.
- Expected: Exactly 100 distinct rows and one completed export record.
- Failure disposition: Block handoff and retain fixture output for diagnosis.
- Evidence capture: Store command, fixture hash, result hash, and timestamp in Magia validation evidence.
- Residual risk disposition: Record unknown production-scale variance as an unresolved operational risk.

### VAL-002 - Resume after interruption
- Requirements: REQ-001
- Acceptance: AC-002
- Tasks: task002
- Environment: Integration environment with worker termination control.
- Command or procedure: Terminate the worker after checkpoint two and start a replacement worker.
- Expected: Resume from checkpoint two without duplicate output rows.
- Failure disposition: Block handoff and require checkpoint design revision.
- Evidence capture: Store checkpoint hashes, output hashes, process events, and command transcript.
- Residual risk disposition: Escalate storage outage behavior to the operational review if not reproduced.

### VAL-003 - Invalid checkpoint and recovery objective
- Requirements: REQ-001
- Acceptance: AC-003
- Tasks: task003
- Environment: Integration environment with invalid-checkpoint fixtures and timing capture.
- Command or procedure: Attempt resume with a mismatched checkpoint and measure valid restart recovery time.
- Expected: Invalid checkpoint is rejected safely and valid recovery completes within the NFR threshold.
- Failure disposition: Block handoff for unsafe acceptance or threshold breach.
- Evidence capture: Store sanitized diagnostic, timing series, fixture hash, and exit status.
- Residual risk disposition: Any untested storage failure remains explicitly blocked before production rollout.
