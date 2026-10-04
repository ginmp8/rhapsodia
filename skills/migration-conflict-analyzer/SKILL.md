---
name: migration-conflict-analyzer
description: Use when asked to analyze Entity Framework Core (.NET) migration .cs files, repository paths, Git diffs, pull requests or PRs, or pasted migration code for schema conflicts, ordering hazards, data-loss or destructive changes, duplicate operations or migration lineage conflicts, ModelSnapshot divergence, raw SQL or reviewed SQL/deployment SQL drift, provider-specific SQL Server/PostgreSQL/SQLite risks, EF Core version-dependent runtime migration/deployment hazards including concurrent Database.Migrate or Database.MigrateAsync, and expand/contract compatibility. Do not use for generic EF Core tutorials, general database design, or ordinary application code review unless migration-specific conflict or deployment-risk analysis is requested.
---

# Migration Conflict Analyzer

## Purpose

Analyze EF Core migration changes as a version-aware, provider-aware, evidence-producing `research-analytic` workflow. Preserve a portable static core that works without the .NET SDK; use optional semantic evidence or provider SQL only when available.

Do not infer production safety from static analysis. Separate observed/derived facts from bounded heuristic judgment and keep `confidence`, `evidence_status`, and `uncertainty` explicit.

## Reproducibility contract

Mechanically reproducible surfaces:

- exact file, Git revision, SQL artifact, runtime-code, semantic-evidence, provider-profile, and heuristic hashes;
- canonical `Up`/`Down` operation extraction and ordering;
- versioned heuristic and provider-profile identities;
- stable finding IDs, severity, gate, confidence, evidence status, and hazard type;
- canonical JSON report plus `analysis_receipt`;
- same-input rerun identity for supported static inputs.

Bounded judgment remains for rename intent, data value compatibility, provider/runtime effects not present in evidence, rolling-deployment compatibility, custom operations, and operational lock duration.

The frozen rule contract is `references/heuristic-set.json` version `3.0.0`. Provider facts used for classification are in `references/provider-profiles.json` version `1.0.0`. Do not silently reinterpret rule IDs, severities, gates, or provider semantics; incompatible changes require a version bump and regression re-baseline.

## Modes

Choose exactly one primary mode:

1. **file/directory mode** — analyze migration files/directories and optional support artifacts.
2. **PR/Git mode** — analyze a repository against an explicit base revision; preferred for branch/lineage questions.
3. **manual review mode** — only pasted/incomplete evidence exists; apply the same taxonomy manually and mark executable gates `not-run`.

## Context and optional evidence

Supply context only when known; unknown values must stay unknown.

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --ef-core-version 10.0.0 \
  --provider postgresql \
  --dbcontext AppDbContext \
  --migrations-assembly App.Infrastructure \
  --deployment-method sql-script \
  --deployment-instances multiple \
  --format json
```

Optional evidence:

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --generated-sql generated.sql \
  --reviewed-sql reviewed.sql \
  --deployment-sql deployment.sql \
  --rollback-sql rollback.sql \
  --runtime-code Program.cs \
  --semantic-evidence semantic-evidence.json \
  --format json
```

`semantic-evidence.json` follows `schemas/semantic-evidence.schema.json`. Treat it as supplied evidence, not as proof that this analyzer executed EF tooling.

### PR/Git mode

```bash
python3 -S scripts/migration_conflict_analyzer.py . \
  --git-base origin/main \
  --format json \
  --output migration-conflict-report.json \
  --receipt migration-conflict-analysis-receipt.json
```

Resolve and record requested base, base SHA, HEAD SHA, merge-base SHA, changed-file identities, migration hashes, snapshot identities, and base/head migration-history identities. Working-tree hashes identify analyzed bytes; Git SHAs identify repository revisions.

## Analysis order

1. Resolve one mode, scope, EF version, provider, DbContext/migration assembly, and deployment context.
2. Hash migrations, support files, SQL artifacts, runtime code, semantic evidence, heuristic set, and provider profiles.
3. In Git mode, resolve immutable base/head/merge-base identities before interpreting conflicts.
4. Parse `Up` and `Down` into canonical structured operations scoped by migration identity and context.
5. Compare full migration IDs and lineage; a shared timestamp alone is only a review signal.
6. Apply version-aware runtime classification and provider-specific rules only when the required context is supplied.
7. Bind reviewed SQL and deployment SQL by exact bytes; drift is an artifact-integrity failure, not a semantic comparison.
8. Compare destructive `Up` operations with `Down`; structural recreation does not prove data recovery.
9. Emit stable findings, explicit limitations, gates, and `analysis_receipt`.
10. For output files, preflight path aliases and preserve last-good artifacts on delivery failure.

## Required coverage

Load `references/conflict-heuristics.md` when interpreting findings. Coverage includes:

- duplicate columns/tables/object names and full migration-ID collisions;
- branch/base history and EF11-capability-gated snapshot lineage;
- snapshot divergence signals;
- structured data operations `InsertData`/`UpdateData`/`DeleteData`;
- destructive schema operations and rollback data-restorability review;
- drop/add rename heuristics with explicit uncertainty;
- operation ordering after drop/rename;
- required-column additions and `AlterColumn` nullability/length/precision/type changes;
- indexes, foreign keys, primary/unique/check constraints, and existing-data validation;
- raw SQL mutation, rerun sensitivity, and transaction suppression;
- runtime-dependent migration code such as clock/random/environment/filesystem/network access;
- `ActiveProvider` branching and provider-profile coverage;
- EF-version-aware startup migration/concurrency/transaction hazards;
- SQLite rebuild/idempotent-script constraints;
- generated SQL operational locking signals for supported providers;
- reviewed/generated/deployment SQL identity drift;
- unknown/custom operations as explicit parser-coverage gaps.

## Version/provider discipline

Do not project one EF Core version onto another. Runtime migration locking, transaction behavior, pending-model checks, and lineage capabilities are version-sensitive.

Do not project one provider onto another. `references/provider-profiles.json` contains bounded profiles for SQL Server, PostgreSQL/Npgsql, and SQLite. Unknown providers fall back to generic rules without invented provider behavior.

EF11-specific `LastMigrationId` lineage logic is capability-gated: use it only when snapshot evidence actually contains that identity. Do not assume unreleased/preview behavior from a version string alone.

## Stable severity and gate rules

Severity and gate come only from `references/heuristic-set.json`:

- `critical` / `block`: deterministic identity/artifact/provider-capability conflicts requiring resolution.
- `high` / `review-required`: destructive or strong compatibility/deployment hazards.
- `medium` / `review-required`: plausible provider/data/runtime hazards needing context.
- `low` / `manual-review`: review signals and coverage gaps.
- `info` / `none`: structural observations.

Never promote/downgrade a rule ad hoc to obtain a preferred result.

## Evidence meanings

Every finding must contain stable ID/rule ID, severity, confidence, evidence status, gate, hazard type, exact subjects, reason, smallest safe remediation, validation step, and uncertainty.

- `observed`: directly present in supplied bytes/options.
- `derived`: deterministic relation between observed identities/operations.
- `inferred`: bounded heuristic interpretation.
- `supplied`: explicit external/semantic/deployment evidence.
- `blocked`: semantics cannot be established safely.

## SQL and semantic evidence

Generated SQL is provider evidence only when supplied. Hash it and inspect only bounded patterns; do not claim it was executed.

Reviewed SQL and deployment SQL must match byte-for-byte when the workflow claims the reviewed artifact is the deployment artifact. `artifact.review-execution-drift` does not say which SQL is better; it says the approved/executed identities differ.

Rollback SQL is a first-class identity. A syntactically valid rollback does not prove lost data can be reconstructed.

Optional semantic evidence may report EF version/provider/context, pending-model changes, migration-lock status, or transaction-suppressed commands. Keep provenance and exact file hash in the report.

## Output contract

Use `references/report-contract.md`. JSON conforming to `schemas/analysis-report.schema.json` is canonical.

`no-static-blocker` means only that the frozen static/optional-evidence rules emitted no critical/high/medium finding for the supplied scope. It is never a production-safety guarantee.

## Validation

Package contract:

```bash
python3 -S scripts/validate_contracts.py --skill-root .
```

Frozen analyzer regressions:

```bash
python3 -S evals/run_analyzer_regressions.py \
  --analyzer scripts/migration_conflict_analyzer.py \
  --scenarios evals/analyzer-regression-scenarios.json \
  --expected-heuristics evals/expected-heuristics.json
```

Do not modify frozen expected outcomes merely to make analyzer changes pass. Correct evaluator defects only through explicit invalidation/re-baseline before interpreting candidate results.

## Release discipline

Before changing this package, preserve an immutable baseline and exact source snapshot for material research/evidence bytes. **Freeze evaluator inputs before candidate mutation** and record evaluator hashes. Compare **baseline vs candidate** with the same frozen evaluator where compatible. Validators should emit machine-readable diagnostics/JSON when objective mechanics fail. Keep structural evidence, behavioral evidence, runtime evidence, and semantic-review evidence separate.

Package only the exact frozen candidate after all applicable validators pass; tie the archive to a durable hash/receipt. A post-pass edit invalidates affected evidence and requires revalidation. The package builder may be owned by a host-neutral meta-workflow; this analyzer must not depend on a vendor-private packager.

## Stop conditions

Stop or return a bounded partial result when:

- no migration/diff/snapshot evidence exists;
- Git mode cannot resolve the requested base or repository identity;
- custom helpers hide material semantics and generated/semantic evidence is unavailable;
- a runtime-safety conclusion needs provider/database/data/deployment evidence not supplied;
- heuristic/provider/evaluator identity cannot be established;
- output aliases an analyzed input, evaluator, or receipt;
- the only route to a pass is weakening a frozen severity/gate/evaluator.
