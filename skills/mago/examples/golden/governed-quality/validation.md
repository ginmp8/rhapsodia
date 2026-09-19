# Validation - Filtered export

## Validation Strategy

Validate behavior at contract, integration, security/logging, and performance levels before handoff closure.

## Validation Scope

### VAL-001 - Contract and integration behavior

- Requirements: REQ-001
- Acceptance: AC-001
- Tasks: task001, task002, task003, task004, task005
- Environment: isolated integration environment with the current queue contract
- Command or procedure: run the export API and worker contract/integration suite with omitted and selected fields
- Expected: omitted fields preserve the current response and selected allowed fields appear exactly once
- Failure disposition: block handoff and retain the previous caller behavior

### VAL-002 - Restricted-field and logging behavior

- Requirements: REQ-002
- Acceptance: AC-002
- Tasks: task002, task004, task005
- Environment: isolated integration environment with redacted log capture
- Command or procedure: submit restricted and unknown identifiers and inspect API, queue, worker, and logs
- Expected: requests are denied before export creation and logs contain no customer values
- Failure disposition: block handoff, disable field selection, and route findings to security review

### VAL-003 - Validation latency

- Requirements: REQ-001
- Acceptance: AC-001
- Tasks: task004
- Environment: representative performance fixture with 100 requested identifiers
- Command or procedure: execute 1,000 validation operations after warmup and calculate p95 duration
- Expected: p95 validation duration is at most 25 milliseconds
- Failure disposition: block rollout and profile normalization/lookup cost

## Performance Validation

VAL-003 provides the measurable threshold.

## Final Verification Checklist

- [ ] Contract and integration checks pass.
- [ ] Restricted-field and logging checks pass.
- [ ] Performance threshold passes.
