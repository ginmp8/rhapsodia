# Convergence and Risk-Driven Validation

Validation proves selected technical behavior. Convergence proves that the implementation evidence covers the approved intent without silently changing it.

## Convergence Chain

Evaluate this chain for each bounded requirement or task:

```text
requirements
-> acceptance criteria
-> planned tasks
-> changed files
-> tests and checks
-> validation evidence
```

Use `scripts/validate_convergence.py` with the contract in `assets/templates/convergence-report.json.template`.

## Allowed Statuses

- `satisfied`: current evidence covers the item.
- `partially_satisfied`: some required evidence or implementation is missing.
- `unsatisfied`: implementation or validation contradicts the item.
- `obsolete`: source authority explicitly superseded the item; cite that authority.
- `unverified`: implementation may exist but current evidence is missing.
- `out_of_scope`: the item is explicitly excluded from this run without being silently dropped.
- `planning_change_required`: execution evidence shows approved intent, acceptance criteria, task definition, architecture, public behavior, persistence, or sequencing must change.

MAGIA may emit a technical-gap handoff for `planning_change_required`; it must not rewrite the planning source. Governed closure requires every in-scope item to be `satisfied` or explicitly accepted by the owning authority outside MAGIA.

## Risk Inputs

Select validation from changed evidence, not generic habit. Inspect:

- file types and generated/source relationships;
- changed components and dependency boundaries;
- public API, event, schema, file, and interface contracts;
- persistence, migrations, transactions, and data transforms;
- authentication, authorization, secrets, and PII;
- concurrency, ordering, idempotency, retries, and messaging;
- performance-sensitive paths and resource limits;
- observability, infrastructure, configuration, and rollout;
- rollback complexity and blast radius.

Use `scripts/select_validation.py` only for preliminary inference from a JSON change descriptor containing changed files or risk signals. It emits `kind: magia-risk-profile-selection` and a minimum profile. Once explicit surfaces and available checks are known, hand selection to the canonical `scripts/select_validation_checks.py` contract in `references/validation-selection.md`; repository-specific commands remain evidence to discover and run.

## Risk-to-Check Matrix

| Risk class | Minimum checks |
|---|---|
| localized code or docs | targeted test or static check; syntax/link/package check as applicable |
| shared code or normal feature | targeted tests, build/type/lint as applicable, regression check |
| public contract | contract/schema compatibility tests, consumer impact review, smoke check |
| persistence or migration | migration validation, expand-contract review, data/rollback check, integration test |
| auth, secrets, PII, security | authorization/security checks, secret-safe logs, negative tests, least-privilege review |
| concurrency or messaging | ordering/idempotency/retry tests, race or duplicate-delivery reasoning, operational signals |
| performance | representative benchmark or load check, limits, regression comparison |
| observability or infrastructure | configuration/static validation, deployment/smoke/operational verification, rollback |
| multi-repository | per-repository checks, compatibility-window checks, cross-repository evidence |

A check can be `not-run` only with a concrete reason and residual risk. Not-run evidence never becomes a pass.

## Evidence Compression

Keep complete evidence without repeating raw output:

1. one machine-readable execution summary using `assets/templates/execution-summary.json.template`;
2. focused implementation notes describing actual changes and decisions;
3. focused validation evidence listing commands, results, and gaps;
4. migration, contract, security, observability, runbook, or troubleshooting documents only when triggered;
5. references to stored logs or command summaries instead of copied output;
6. redaction of secrets, credentials, PII, tokens, cookies, and sensitive logs.

Human closure should summarize the decision-relevant evidence and point to durable records. It should not reproduce the run-state document or command transcript.
