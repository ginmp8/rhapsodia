# Review Workflow

Use this reference for every substantive bug/security hunt.

## Investigation loop

1. **Target**: name the artifact or flow under review.
2. **Baseline**: identify intended behavior, normal event sequence, expected state changes, and existing tests or observability.
3. **Trust boundaries**: identify where input, identity, tenant, permissions, secrets, data, or execution context crosses a boundary.
4. **Invariants**: define properties that must remain true after retries, concurrency, failures, and malicious inputs.
5. **Hypotheses**: generate bounded claims such as "duplicate event can create duplicate side effect" or "consumer trusts tenantId from payload".
6. **Evidence pass**: inspect the smallest relevant code/config/logs first. Do not jump to broad rewrites.
7. **Stress pass**: test or propose stress around the highest-risk hypothesis.
8. **Decision**: confirm, reject, or mark each hypothesis as needing verification.
9. **Fix plan**: propose the smallest safe fix and exact validation.
10. **Residual risk**: state what remains uninspected.

## Evidence labels

- **Confirmed**: directly supported by inspected code/config/output or executed validation.
- **Likely**: supported by strong evidence but missing one confirmation point.
- **Needs verification**: plausible but not yet evidenced enough for a finding.
- **Planned test**: a proposed validation scenario, not evidence.
- **Out of scope**: relevant but not inspected due to target boundaries.

## Finding quality bar

A finding is strong only when it includes:

- location: file/path/function/event/consumer/config when available;
- evidence: exact behavior, code shape, config, or trace signal;
- impact: concrete failure or abuse path;
- smallest fix: local change, control, or test;
- validation: how to prove the fix works.

## Review order

1. Security and data isolation.
2. Data loss, duplication, and irreversible side effects.
3. Message ordering, retries, idempotency, and concurrency.
4. Persistence and transaction boundaries.
5. External dependencies and failure handling.
6. Observability, audit, DLQ, and reprocessing controls.
7. Performance and operational resilience.
8. Maintainability only after high-impact risks are handled.

## Closure criteria

A review can be called complete for the stated scope when:

- all supplied artifacts were inspected or explicitly excluded;
- every critical/high hypothesis is confirmed, rejected with evidence, or left as a named validation gap;
- validation is separated into executed and suggested checks;
- no unsupported claim says the project is bug-free or secure;
- the next action is concrete.
