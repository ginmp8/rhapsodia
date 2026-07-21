# Validation Selection

Load before choosing or reporting validation for non-trivial changes. This reference selects proof categories from execution risk; it does not redefine Mago acceptance criteria, invent repository commands, or convert unavailable checks into passes.

## Selection Principles

1. Start with the narrowest check that can falsify the selected technical objective.
2. Add checks required by affected surfaces and risk triggers.
3. Prefer existing repository validators and conventions over new tooling.
4. Treat build, lint, static analysis, tests, contracts, migration, security, performance, smoke, and manual verification as distinct evidence.
5. Record each applicable check as `pass`, `fail`, `blocked`, `skipped`, or `not-run` with a reason.
6. A passing narrow check does not replace mandatory governed checks.
7. Local validation does not prove deployment or production behavior.

## Deterministic Selector

Provide a temporary JSON request outside canonical evidence:

```json
{
  "surfaces": ["code", "api"],
  "available_checks": ["targeted-test", "contract-validation", "compatibility", "integration"]
}
```

Run:

```text
python scripts/select_validation_checks.py --input <request.json> --format json
```

The selector emits:

- risk profile;
- required and recommended check categories;
- narrowest proving category;
- required categories missing from `available_checks`;
- explicit limitations.

It never executes checks or emits a success result.

## Surface Vocabulary

- `docs`: documentation-only change;
- `code`: bounded implementation or refactor;
- `config`: configuration or infrastructure-adjacent change;
- `api`, `event`, `schema`: external or shared contract surfaces;
- `migration`: schema/data migration or persisted-data transformation;
- `auth`: authentication or authorization behavior;
- `secrets`, `pii`: sensitive data or credential handling;
- `performance`: latency, throughput, capacity, or resource usage;
- `availability`: retry, recovery, failover, degradation, or operational continuity;
- `multi-repo`: coordinated execution across repositories or services.

Unknown surfaces block selection instead of silently degrading to code-only validation.

## Closure

Before completion, map concrete commands or methods to every required category, run what is safe and available, and preserve missing categories as blockers or residual risk. Do not mark the work done when a critical contract, migration, security, recovery, or authority check remains unresolved.
