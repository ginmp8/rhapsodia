# Change Sequencing and PR Splitting

Use this file when converting a context map into an implementation plan.

## Safe sequencing principles

1. Read primary files immediately before editing.
2. Modify low-level contracts before call sites only when the compiler or tests will clearly expose remaining usages.
3. For public APIs, prefer compatibility layers before removals.
4. Add tests before or alongside behavior changes when the expected behavior is clear.
5. Run targeted validation after each coherent batch.
6. Keep mechanical refactors separate from behavior changes when review risk is high.

## Common sequences

### Bugfix

1. Reproduce or identify failing behavior.
2. Add or adjust a focused test if feasible.
3. Patch the smallest responsible unit.
4. Run targeted test and adjacent tests.
5. Check callers for changed assumptions.

### Feature

1. Identify existing analogous feature.
2. Add or update contracts, DTOs, schema, or configuration.
3. Implement core behavior.
4. Wire runtime registration or routing.
5. Add tests at the same layer as comparable features.
6. Update docs or examples if behavior is user-facing.

### Refactor

1. Freeze behavior with tests or compile checks.
2. Move or rename in a mechanical pass.
3. Update imports, registrations, and generated references.
4. Run validation.
5. Apply behavior changes only after the mechanical pass is stable.

### Migration or schema change

1. Prefer expand-contract: add compatible schema first.
2. Update writers.
3. Backfill or dual-read if needed.
4. Update readers.
5. Remove old fields only after compatibility evidence exists.

## PR split triggers

Recommend splitting when the plan includes:

- schema plus application logic plus cleanup;
- public contract changes plus broad call-site rewrites;
- generated code plus hand-written implementation;
- mechanical rename plus behavior change;
- unrelated domains, services, or ownership boundaries.

## Validation ladder

1. Static checks: formatting, linting, type checking, compile.
2. Focused tests: test file nearest the changed behavior.
3. Integration tests: cross-module wiring and runtime contracts.
4. End-to-end or smoke tests: user-visible flows.
5. Operational checks: logs, metrics, alerts, migration dry runs, rollback plan.
