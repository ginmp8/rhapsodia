# Change Sequencing and PR Splitting

Use this file when converting a context map into implementation work.

## Pre-edit freshness gate

Before the first edit:

1. Verify the approved map still refers to the current repository state.
2. Re-read all primary files and critical secondary files, or verify a previously captured evidence manifest.
3. If a leaf changed, refresh that branch. If a central contract/schema/generator/runtime registration changed, refresh the wider graph.
4. Record material map drift before expanding scope.

## Safe sequencing principles

1. Change the owning source before derived outputs when the repository has a generator/build step.
2. Modify low-level contracts before call sites only when compiler/tests or explicit searches will expose remaining consumers.
3. For public APIs and data contracts, prefer compatibility layers/expand-contract before removals when feasible.
4. Add tests before or alongside behavior changes when expected behavior is established.
5. Run targeted validation after each coherent batch.
6. Keep mechanical refactors separate from behavior changes when review risk is high.
7. Re-run consumer searches after contract/rename changes to detect missed references.

## Common sequences

### Bugfix

1. Reproduce or establish the failing behavior.
2. Add/adjust a focused test when feasible.
3. Patch the smallest owning unit.
4. Run targeted and adjacent tests.
5. Re-check callers for changed assumptions.

### Feature

1. Identify owning contract/source and an analogous feature.
2. Add/update contracts, DTOs, schema, or configuration.
3. Implement core behavior.
4. Wire runtime registration/routing.
5. Add tests at comparable layers.
6. Update docs/examples when user-facing.

### Refactor

1. Freeze behavior with tests/compile checks or explicit observable invariants.
2. Perform mechanical move/rename.
3. Update imports, registrations, generated references, and dynamic names.
4. Validate.
5. Apply behavior changes only after the mechanical pass is stable.

### Migration or schema change

1. Add compatible schema/contract first.
2. Update writers.
3. Backfill/dual-write/dual-read when needed.
4. Update readers and downstream consumers.
5. Validate migration and rollback/recovery.
6. Remove old fields only after compatibility evidence exists.

## PR split triggers

Recommend splitting when work includes:

- schema plus application logic plus cleanup;
- public contract changes plus broad call-site rewrites;
- generated code plus generator/source changes;
- mechanical rename plus behavior change;
- unrelated domains, services, ownership boundaries, or independent rollback units.

## Validation ladder

1. Static checks: formatting, linting, type checking, compile.
2. Focused tests: nearest changed behavior.
3. Integration/contract tests: cross-module/runtime wiring.
4. End-to-end/smoke tests: user-visible flows.
5. Operational checks: logs, metrics, alerts, migration dry runs, rollout/rollback.

Report each validation result as measured, observed, planned, or blocked. Never convert planned validation into a pass.
