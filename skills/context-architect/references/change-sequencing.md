# Change Sequencing and PR Splitting

Use this file when converting a context map into implementation work.

## Pre-edit freshness gate

Before the first edit:

1. Verify the approved map still refers to the current repository state and, for review-impact, the same base/head or changed-file anchor.
2. Re-read all primary files and critical secondary files, or verify a previously captured evidence manifest.
3. If a leaf changed, refresh that branch. If a central contract/schema/generator/runtime registration/build graph changed, refresh the wider graph.
4. If a lockfile/resolved dependency version changed and external API behavior is material, refresh the affected external-version branch.
5. Record material map drift before expanding scope.

## Safe sequencing principles

1. Change the owning source before derived outputs when the repository has a generator/build step.
2. Modify low-level contracts before call sites only when semantic/build/compiler checks, tests, or explicit searches will expose remaining consumers.
3. For public APIs and data contracts, prefer compatibility layers/expand-contract before removals when feasible.
4. Add tests before or alongside behavior changes when expected behavior is established.
5. Run targeted validation after each coherent batch.
6. Keep mechanical refactors separate from behavior changes when review risk is high.
7. Re-run direct and reverse consumer searches after contract/rename changes to detect missed references.
8. Run selective data-flow/runtime analysis only when an extended-tier source-to-sink/behavior branch remains open; do not make it a universal precondition.

## Common sequences

### Bugfix

1. Reproduce or establish the failing behavior.
2. Add/adjust a focused test when feasible.
3. Patch the smallest owning unit.
4. Run targeted and adjacent tests.
5. Re-check direct/reverse callers for changed assumptions.

### Feature

1. Identify owning contract/source and an analogous feature.
2. Add/update contracts, DTOs, schema, or configuration.
3. Implement core behavior.
4. Wire runtime/build registration/routing.
5. Add tests at comparable layers.
6. Update docs/examples when user-facing.

### Refactor

1. Freeze behavior with tests/compile checks or explicit observable invariants.
2. Perform mechanical move/rename.
3. Update imports, registrations, generated references, dynamic names, and reverse dependents.
4. Validate.
5. Apply behavior changes only after the mechanical pass is stable.

### Migration or schema change

1. Add compatible schema/contract first.
2. Update writers.
3. Backfill/dual-write/dual-read when needed.
4. Update readers and downstream consumers.
5. Validate migration and rollback/recovery.
6. Remove old fields only after compatibility evidence exists.

### External dependency/version change

1. Freeze current and proposed resolved versions/lockfile evidence.
2. Identify local call sites and wrappers using the external API.
3. Inspect version-specific external contract/source/docs when available.
4. Apply compatibility/adaptation changes before removing old paths.
5. Run focused tests against the resolved dependency environment.
6. Recompute affected project/reverse-dependent scope when the build system supports it.

## PR split triggers

Recommend splitting when work includes:

- schema plus application logic plus cleanup;
- public contract changes plus broad call-site rewrites;
- generated code plus generator/source changes;
- mechanical rename plus behavior change;
- dependency-version migration plus unrelated cleanup;
- unrelated domains, services, ownership boundaries, or independent rollback units.

## Validation ladder

1. Static checks: formatting, linting, type checking, compile.
2. Focused tests: nearest changed behavior.
3. Integration/contract tests: cross-module/runtime wiring.
4. End-to-end/smoke tests: user-visible flows.
5. Operational checks: logs, metrics, alerts, migration dry runs, rollout/rollback.
6. Context-selection metrics: only when a frozen gold/reference context exists; report separately from code/test correctness.

Report each validation result as measured, observed, planned, or blocked. Never convert planned validation into a pass.
