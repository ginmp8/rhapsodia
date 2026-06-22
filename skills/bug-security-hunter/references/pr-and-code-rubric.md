# PR and Code Rubric

Use this reference for PRs, diffs, snippets, and repository areas. Review objectively, proportionally to risk, and from inspected evidence. Do not create findings from personal style preference alone.

## PR review sequence

1. Identify the behavioral change introduced by the PR, using title, description, issue/card, diff, tests, and validation evidence when available.
2. Map impacted areas: functional behavior, scope, design, tests, security, performance, reliability, database, APIs, messaging, jobs, observability, deployment, rollback, and operations.
3. Trace each changed entry point to state changes, external calls, events, logs, permissions, transactions, retries, and error handling.
4. Compare old and new behavior for regressions, broadened permissions, changed defaults, changed contracts, and changed failure modes.
5. Inspect tests and manual validation for meaningful coverage of new behavior, edge cases, permissions, failure paths, migrations, logs, and rollback.
6. Classify each material issue by severity, evidence confidence, merge-blocking status, and expected treatment.

## Review dimensions adapted from PR review discipline

### Functional correctness

Verify that the change solves the stated problem, follows the business rule, handles edge cases, avoids regressions, and does not depend on unvalidated assumptions, fragile ordering, duplicated data, stale data, concurrency luck, retries, or implicit behavior absent from the PR contract.

### Scope control

Check whether the PR stays focused or mixes feature work, bug fixes, refactors, formatting, dependency changes, migrations, and operational changes without a clear reason. A large PR is not automatically wrong; the risk appears when objective, files, and validation do not allow a safe review.

### Design and maintainability

Evaluate simplicity, naming clarity, responsibility boundaries, coupling, meaningful duplication, repository conventions, testability, and accidental complexity. Raise design findings only when evidence shows concrete maintenance risk, rule hiding, divergence risk, broken local patterns, or reduced testability.

### Tests and validation

Look for tests covering new behavior, regressions, error cases, permissions, limits, invalid inputs, edge cases, migrations, contracts, and integration boundaries. Flag weak tests when they assert implementation details, rely on mocks that hide critical integration risk, use unrealistic fixtures, or lack observable behavior checks.

### Performance and scalability

Inspect unbounded queries, excessive loading, hot-path loops, sequential external calls, N+1 access, locks, contention, missing timeouts, memory pressure, CPU pressure, database load, queue load, and API rate limits. Consider pagination, batching, caching, indexes, limits, streaming, and backpressure where volume can grow.

### Reliability and operations

Inspect error handling, timeout, retry, idempotency, fallback, partial failure handling, logs, metrics, traces, progressive deployment, rollback, supportability, troubleshooting, and consistency across database, messaging, cache, and external APIs. Raise operational risk when production behavior would be hard to predict or diagnose.

### Database and migrations

Review data loss, long locks, breaking schema changes, constraints, indexes, required columns without safe defaults, renames, removals, backfills, query impact, progressive rollout, and expand-contract compatibility. Consider whether old and new application versions can coexist during deployment.

### APIs, contracts, messaging, and jobs

Check breaking changes, new required fields, semantic changes to existing fields, status codes, error shapes, versioning, client compatibility, consumer compatibility, webhooks, events, queues, background jobs, schedulers, and replay/reprocessing paths. Flag changes that need communication, versioning, fallback, or compatibility strategy.

### Security review discipline

Review source, configuration, IaC, CI/CD, scripts, Dockerfiles, manifests, tests, fixtures, sample payloads, documentation, and logs. Prioritize secrets, sensitive logging, authn/authz, tenant/resource ownership, injection, unsafe deserialization, SSRF, path traversal, client-side secret leakage, broad pipeline permissions, risky dependencies, and unpinned runtime artifacts. Mask sensitive values; recommend rotation, revocation, log/history audit, and least privilege when exposure is likely or confirmed.

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

## Severity, verdict, and expected treatment

Severity is not the same as the merge verdict. Severity describes risk. The merge verdict describes whether the PR can merge. Expected treatment describes what should happen next.

Severity guidance:

- **Critical/High**: normally blocks merge unless the team explicitly accepts the risk with a documented mitigation and the risk is not a real secret exposure, relevant data loss, authorization bypass, or breaking contract.
- **Medium**: often requires a fix before merge when it affects core behavior, security posture, data integrity, or operations; otherwise it may be accepted with explicit follow-up.
- **Low**: non-blocking improvement, readability, minor edge case, or test/telemetry gap.
- **Needs verification**: a question that affects approval because evidence is missing or ambiguous.

Expected treatment options:

- Fix in this PR.
- Already fixed by the author in this PR.
- Accepted by the team without change.
- Future issue opened for follow-up.
- Not applicable.

A future issue does not lower severity. A blocker remains a blocker unless an explicit team decision accepts the risk and the risk is safe to defer.

## PR verdict guide

- **Blocked** when critical/high findings remain, tests fail, authorization/data integrity is unproven on changed critical paths, secrets appear real, destructive migrations lack a safe plan, contracts break without compatibility, or rollback is unclear for irreversible effects.
- **Needs more context** when essential diff, changed files, validation, migration details, security context, or operational evidence is missing and prevents a safe decision.
- **Approve with reservations** when only medium/low findings remain and mitigation, ownership, or follow-up is explicit.
- **Approve** only when no blocking issues are found in the inspected scope and validation is adequate for the risk.

## Suggested PR comment guidance

When the user asks for comments to post, keep each suggested PR comment short, evidence-linked, and actionable. Include severity and the smallest requested change. Do not include full secrets or sensitive values. Use comments only for findings that would help the author act; keep broader reasoning in the review summary.
