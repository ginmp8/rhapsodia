# PR and Code Rubric

Use this reference for PRs, diffs, snippets, and repository areas.

## PR review sequence

1. Identify the behavioral change introduced by the PR.
2. Trace each changed entry point to state changes, external calls, events, logs, and error handling.
3. Compare old and new behavior for regressions, broadened permissions, changed defaults, and changed failure modes.
4. Inspect tests for meaningful coverage of new behavior and edge cases.
5. Classify findings as blockers, required fixes, or optional improvements.

## Language-neutral bug patterns

- input validation accepts invalid, missing, malformed, oversized, duplicated, stale, or cross-tenant data;
- authorization is checked in the caller but not at the callee/consumer;
- state transition allows impossible, regressive, or terminal-state-changing transitions;
- side effect happens before durable state or before authorization is complete;
- transaction boundary excludes related side effects;
- retry can duplicate an external call or message;
- errors are swallowed, converted to success, or logged without actionable context;
- cleanup/finally code hides original failures;
- time, timezone, culture, ordering, random, and clock dependencies are implicit;
- batch, pagination, or streaming code drops, duplicates, or partially processes items;
- configuration defaults are unsafe or differ across environments;
- test fixtures assert implementation details but not observable behavior.

## Integration and data hazards

- schema evolution: consumers assume fields always exist or enums never change;
- database: missing unique constraints for idempotency, broad updates/deletes, weak isolation, missing indexes for hot paths;
- cache: stale data can authorize, duplicate, or suppress work incorrectly;
- external APIs: no timeout, cancellation, retry limit, idempotency key, or response validation;
- files/storage: path traversal, unsafe object keys, unbounded size, missing content-type validation;
- observability: correlation lost, sensitive payload logged, missing audit for privileged decisions.

## PR verdict guide

- **Block merge** when critical/high findings remain, tests fail, authorization/data integrity is unproven on changed critical paths, or rollback is unclear for irreversible effects.
- **Approve with reservations** when only medium/low findings remain and mitigation or follow-up is explicit.
- **Approve** only when no blocking issues are found in the inspected scope and validation is adequate for the risk.
