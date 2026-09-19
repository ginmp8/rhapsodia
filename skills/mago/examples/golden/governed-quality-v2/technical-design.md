# Technical Design - Governed Quality V2

### OPTION-001 - Durable chunk checkpoint
- Benefits: Precise resume boundary and bounded replay.
- Costs: Additional checkpoint writes and cleanup.
- Failure modes: Stale checkpoint or storage unavailability.
- Operational impact: Checkpoint latency and age require metrics.

### OPTION-002 - Restart full export
- Benefits: Simpler worker state.
- Costs: Repeats completed work and increases capacity demand.
- Failure modes: Duplicate output if downstream replacement is not atomic.
- Operational impact: Longer recovery and burst capacity.

### DECISION-001 - Use durable chunk checkpoints
- Requirements: REQ-001
- Selected option: OPTION-001
- Rationale: It bounds replay while preserving exactly-once output semantics.
- Consequences: Checkpoint storage becomes part of the recovery path.
- Rollback or reversibility: Disable checkpoint resume and return to full restart only after draining active exports and validating duplicate prevention.
