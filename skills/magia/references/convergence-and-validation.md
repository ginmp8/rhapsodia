# Deterministic Convergence and Risk-Driven Validation

Load before validation planning and close. Completion must be traceable, not narrative.

## Convergence

```text
requirements/objective -> acceptance criteria -> tasks -> changed files -> checks -> evidence
```

Create one item per requirement or bounded ADHOC objective. Statuses:

- `satisfied`: current implementation/evidence covers it;
- `partially_satisfied`: required behavior/evidence is missing;
- `unsatisfied`: absent or contradicted;
- `obsolete`: superseded with authoritative evidence;
- `unverified`: implementation may exist but evidence is insufficient;
- `out_of_scope`: excluded by selected scope with reason;
- `planning_change_required`: code evidence requires Mago to change intent, criteria, tasks, sequence, architecture, contract, or data model.

Every modified file maps to an item and an applicable check. Completion requires every in-scope item `satisfied`, no unverified file, current evidence, and no unresolved planning change. Validate with `scripts/validate_convergence.py`.

## Risk Selection

Classify current changes by file/generated types, components/dependencies, public API/event/schema/interface contracts, persistence/migrations/caches/data repair, auth/authz/secrets/PII/compliance, concurrency/idempotency/order/retries, performance/resource limits, messaging/observability/infrastructure/deployment, rollback complexity, and cross-service/repo compatibility.

```bash
python scripts/select_validation_profile.py --input <change-facts.json> --json
```

The selector returns strictest profile, reasons, checks, documentation triggers, run-state need, and rollback expectation.

Required checks by signal:

- localized docs/config/code: focused check; syntax/build when applicable;
- normal feature/bug/refactor: targeted tests, applicable build/lint/static, regression, smoke;
- public/API/event/schema: contract tests, compatibility/consumer evidence, smoke;
- persistence/migration: migration and forward/backward compatibility, data-loss review, rollback;
- auth/authz/secrets/PII/compliance: security and negative-auth tests, redaction, permission/secret evidence;
- concurrency/order: concurrency/property plus retry/duplicate/reordering checks;
- performance: representative check or explicit `not_run` risk with baseline/limit evidence;
- messaging/observability/infrastructure: build/static, smoke, operational and rollback/runbook evidence;
- cross-service/repo or difficult rollback: governed profile, full relevant suite, compatibility window, per-repo checkpoints/rollback.

`not_run` requires a concrete reason/residual risk and does not satisfy governed work unless equivalent current evidence is named and accepted.

## Close Gate

Run selected checks; validate convergence; verify run-state hashes when resumable/governed; sync truthful records; hand planning/governance changes to Mago/nomia; emit concise, redacted evidence.
