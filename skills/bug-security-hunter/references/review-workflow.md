# Review Workflow

Use this reference for every substantive bug/security hunt.

## Investigation loop

1. **Target**: name the artifact or flow under review.
2. **Identity and baseline**: record target/source identity, revision or supplied artifact identity, intended behavior, normal event sequence, expected state changes, and existing tests or observability.
3. **Trust boundaries**: identify where input, identity, tenant, permissions, secrets, data, or execution context crosses a boundary.
4. **Invariants**: define properties that must remain true after retries, concurrency, failures, and malicious inputs.
5. **Hypotheses**: generate at most eight open falsifiable claims per pass unless separate evidence supports additional high-risk branches. Deduplicate by root cause and affected subject.
6. **Aggressive evidence pass**: inspect the smallest relevant code/config/logs first, but do not stop at the happy path. For PRs, deliberately check changed files, nearby callers/callees, tests, configs, migrations, CI/CD, Docker/manifests, scripts, sample payloads, logs, and docs when supplied. Do not jump to broad rewrites.
7. **Stress pass**: test or propose stress around the highest-risk hypothesis. Prefer hypotheses that can reveal security bypass, data exposure, data loss, duplicate side effects, broken contracts, replay/retry bugs, production instability, or irreversible rollback risk.
8. **Decision**: confirm, reject, merge as duplicate, block, or mark each hypothesis as needing verification. Stop a branch after two consecutive validation attempts add no discriminating evidence unless new evidence changes the test.
9. **Fix plan**: propose the smallest safe fix and exact validation.
10. **Residual risk**: state what remains uninspected.

## Evidence status and confidence

Keep evidence provenance separate from conclusion confidence.

Evidence status:

- **measured**: executed command/test/scan/replay/runtime evidence;
- **observed**: directly inspected source/diff/config/log/artifact;
- **supplied**: user-provided or external result not independently reproduced;
- **inferred**: conclusion derived from evidence but not directly demonstrated;
- **planned**: proposed validation, not executed evidence;
- **blocked**: relevant evidence could not be obtained;
- **out-of-scope**: deliberately excluded from the declared review surface.

Confidence:

- **confirmed**: the defect/control gap is directly established for the stated scope;
- **likely**: strong support with one material confirmation point missing;
- **needs-verification**: evidence is insufficient and can change the review decision;
- **not-applicable**: confidence is not meaningful for that dimension.

Static source inspection is `observed`, not `measured`. A `needs-verification` item is normally a `QUESTION` or validation gap rather than a confirmed finding.

## Finding quality bar

A finding is strong only when it includes:

- location: file/path/function/event/consumer/config when available;
- evidence: exact behavior, code shape, config, or trace signal;
- impact: concrete failure or abuse path;
- smallest fix: local change, control, or test;
- validation: how to prove the fix works;
- evidence status and confidence;
- severity rationale and root-cause fingerprint for deduplication.

## Severity display

Use the visual label on every user-facing finding and PR comment:

- 🔴 `BLOCKER`: merge-blocking critical/high risk or unresolved severe failure mode.
- 🟠 `MAJOR`: should be fixed before merge unless the team explicitly accepts the risk.
- 🟡 `MINOR`: recommended non-blocking improvement or bounded risk.
- 🔵 `NIT`: small readability, style, naming, or consistency issue only.
- 🟣 `QUESTION`: approval-relevant uncertainty or suspicious signal that needs verification.

Do not downgrade severity because a future issue exists. Do not upgrade a weak hypothesis to a finding without evidence; keep it as 🟣 `QUESTION` or a validation gap. Apply the hard floors and tie-breakers in `reproducible-review-contract.md` before final ordering.

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
- every critical/high hypothesis is confirmed, rejected with evidence, merged as duplicate, blocked explicitly, or left as a named validation gap;
- validation is separated into measured, supplied, planned, and blocked checks;
- findings are deduplicated and sorted using the canonical ordering contract;
- no unsupported claim says the project is bug-free or secure;
- the next action is concrete.
