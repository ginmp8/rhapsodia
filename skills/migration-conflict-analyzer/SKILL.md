---
name: migration-conflict-analyzer
description: Use when asked to analyze Entity Framework Core (.NET) migration .cs files, repository paths, Git diffs, pull requests or PRs, or pasted migration code for schema conflicts, ordering hazards, data-loss or destructive changes, duplicate operations or migration lineage conflicts, ModelSnapshot divergence, raw SQL or reviewed SQL/deployment SQL drift, provider-specific SQL Server/PostgreSQL/SQLite risks, EF Core version-dependent runtime migration/deployment hazards including concurrent Database.Migrate or Database.MigrateAsync, and expand/contract compatibility. Do not use for generic EF Core tutorials, general database design, or ordinary application code review unless migration-specific conflict or deployment-risk analysis is requested.
---

# Migration Conflict Analyzer

## Control plane

Analyze EF Core migration changes as a version-aware, provider-aware, evidence-producing `research-analytic` workflow. The portable static core must work without the .NET SDK; semantic evidence and provider SQL are optional evidence, never assumed execution proof. Do not infer production safety from static analysis.

Use this skill for migration-specific conflict/deployment-risk analysis. Do not use it for generic EF Core education, general schema design, or ordinary code review without a migration-specific risk question.

### Choose exactly one mode

1. **file/directory** — migration files/directories plus optional supporting artifacts.
2. **PR/Git** — repository against an explicit base revision; preferred for branch/history/lineage questions. Load `references/pr-workflow.md`.
3. **manual review** — pasted/incomplete evidence only; use the same taxonomy and mark executable gates `not-run`.

Unknown context stays unknown. Never invent EF version, provider, DbContext, migrations assembly, deployment topology, database contents, or runtime evidence.

### Non-negotiable invariants

- Frozen rule authority: `references/heuristic-set.json` v`3.0.0`; provider facts: `references/provider-profiles.json` v`1.0.0`. Never reinterpret rule IDs, severity, gate, or provider semantics ad hoc; incompatible changes require versioning and regression re-baseline.
- Version/provider discipline: do not project one EF Core version or provider onto another. Unknown providers get generic rules only. EF11 `LastMigrationId` lineage is capability-gated by actual snapshot evidence, not version string alone.
- Identity discipline: hash analyzed migration/support/runtime/semantic/SQL inputs plus heuristic/provider contracts. In Git mode resolve requested base, base SHA, HEAD SHA, merge-base SHA, history identities, and working-tree bytes separately.
- Migration identity is the full migration ID; a shared timestamp alone is only a review signal. Scope identity by DbContext + migrations assembly when available, otherwise by the strongest available migration-set/directory evidence.
- Artifact integrity: reviewed SQL and deployment SQL must be byte-identical when review/execution identity is claimed. Generated, reviewed, deployment, and rollback SQL are distinct first-class identities.
- Destructive rollback: recreating a dropped column/table in `Down` does not prove original data recovery.
- Evidence classes: `observed` = supplied bytes/options; `derived` = deterministic relation; `inferred` = bounded heuristic judgment; `supplied` = explicit external/semantic/deployment evidence; `blocked` = semantics cannot be established safely.
- Every finding carries stable ID/rule ID, severity, confidence, evidence status, gate, hazard type, exact subjects, reason, smallest safe remediation, validation step, and uncertainty.
- Severity/gate come only from the frozen heuristic set: `critical/block`, `high/review-required`, `medium/review-required`, `low/manual-review`, `info/none`.
- Canonical output is JSON conforming to `schemas/analysis-report.schema.json` plus `analysis_receipt`. `no-static-blocker` means only no critical/high/medium finding from supplied static/optional evidence; it is never a production-safety guarantee.

### Start correctly

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --ef-core-version 10.0.0 --provider postgresql \
  --dbcontext AppDbContext --migrations-assembly App.Infrastructure \
  --deployment-method sql-script --deployment-instances multiple --format json
```

Add optional evidence only when it exists: `--generated-sql`, `--reviewed-sql`, `--deployment-sql`, `--rollback-sql`, `--runtime-code`, `--semantic-evidence`. Treat semantic evidence as supplied evidence, not proof this analyzer executed EF tooling.

For Git mode use `--git-base <revision>` and record immutable Git identities before interpreting conflicts.

### Analysis order

1. Resolve one mode, scope, known EF/provider/context, and deployment context.
2. Freeze/hash migrations, support files, SQL, runtime code, semantic evidence, heuristic set, and provider profiles.
3. In Git mode resolve base/head/merge-base and history identities first.
4. Parse `Up`/`Down` into canonical operations scoped by migration identity/context.
5. Compare full migration IDs, branch/base history, snapshot lineage, and changed bytes.
6. Apply version-aware runtime and provider-specific rules only when required context exists.
7. Bind SQL artifact identities; classify drift as artifact-integrity evidence, not semantic superiority.
8. Compare destructive `Up` with `Down`; keep data restorability separate from structural inversion.
9. Emit stable findings, limitations, gates, uncertainty, canonical report, and receipt.
10. Preflight output aliases and preserve last-good artifacts on delivery failure.

### Required coverage and direct references

Load `references/conflict-heuristics.md` when interpreting findings. It covers identity/lineage, snapshot divergence, structured data mutations, destructive changes, rollback restorability, rename/order hazards, column narrowing/nullability/type changes, indexes/keys/constraints, raw SQL and transaction suppression, runtime-dependent migration code, provider branching, EF runtime migration concurrency/transaction hazards, SQLite rebuild/idempotent-script constraints, generated-SQL locking signals, SQL artifact drift, and unknown/custom operation gaps.

- `references/pr-workflow.md` — exact Git/PR lineage workflow and validation hierarchy.
- `references/report-contract.md` — canonical report decisions, receipts, and evidence-layer claims.
- `references/heuristic-set.json` — machine authority for rules/severity/gates/hazard types.
- `references/provider-profiles.json` — bounded SQL Server, PostgreSQL/Npgsql, and SQLite provider facts.
- `schemas/semantic-evidence.schema.json` — optional host-neutral EF-aware evidence contract.
- `examples/migration-review-examples.md` — calibrated review examples; never overrides rule authority.

### Stop conditions

Return a bounded partial result rather than overclaim when there is no migration/diff/snapshot evidence; Git base/repository identity cannot be resolved; custom helpers hide material semantics without generated/semantic evidence; runtime safety needs missing provider/database/data/deployment evidence; heuristic/provider/evaluator identity cannot be established; output aliases an analyzed input/evaluator/receipt; or passing would require weakening a frozen severity/gate/evaluator.

## Reproducibility contract

Mechanically reproducible surfaces are exact input/revision/artifact hashes; canonical `Up`/`Down` extraction and ordering; versioned heuristic/provider identities; stable finding IDs/severity/gate/confidence/evidence status/hazard type; canonical JSON plus receipt; and same-input rerun identity for supported static inputs.

Bounded judgment remains for rename intent, data value compatibility, provider/runtime effects absent from evidence, rolling-deployment compatibility, custom operations, and operational lock duration.

## Context and optional evidence

Supply context only when known; unknown values must stay unknown.

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

`semantic-evidence.json` follows `schemas/semantic-evidence.schema.json`. Keep its provenance and exact hash.

### PR/Git mode

```bash
python3 -S scripts/migration_conflict_analyzer.py . \
  --git-base origin/main \
  --format json \
  --output migration-conflict-report.json \
  --receipt migration-conflict-analysis-receipt.json
```

Working-tree hashes identify analyzed bytes; Git SHAs identify repository revisions. Load `references/pr-workflow.md` for branch reconciliation and validation hierarchy.

## Detailed interpretation rules

Use `references/conflict-heuristics.md`; machine authority remains `references/heuristic-set.json`.

- Required additions and `AlterColumn` nullability/length/precision/store-type changes require data-compatibility review; static analysis never claims actual rows violate the new contract.
- `InsertData`/`UpdateData`/`DeleteData` are first-class data mutations, not a raw-SQL-only concern.
- Raw SQL classification is intentionally bounded; absence of a pattern never proves safety.
- `Database.Migrate`/`MigrateAsync` is a deployment review signal. Multiple-instance classification is EF-version-sensitive; EF9+ migration locking does not prove rolling-deploy compatibility or safe DDL overlap.
- `ActiveProvider` branches are valid but incomplete provider-sensitive branching is a review hazard.
- Runtime-dependent clock/random/environment/filesystem/network use is a determinism review signal, not automatic proof of nondeterministic SQL.
- SQLite provider constraints, provider-specific migration locks, and generated-SQL locking behavior must come from the selected provider profile/evidence.
- Unknown/custom `migrationBuilder` operations remain manual-review coverage gaps; do not guess semantics.

## SQL and semantic evidence

Generated SQL is provider evidence only when supplied. Hash it and inspect bounded patterns; never claim it was executed.

`artifact.review-execution-drift` proves reviewed/executed identities differ; it does not determine which SQL is semantically better. Generated-vs-reviewed drift is likewise identity evidence.

Rollback SQL is a first-class identity. Syntactic rollback validity does not prove lost data reconstruction.

Optional semantic evidence may report EF version/provider/context, pending-model changes, migration-lock status, or transaction-suppressed commands. Keep semantic evidence distinct from static, generated-SQL, and actual runtime/database evidence.

## Output contract

Use `references/report-contract.md`. JSON conforming to `schemas/analysis-report.schema.json` is canonical.

Decision semantics are fixed by the report contract: any `block` -> `block`; otherwise high -> `changes-required`; otherwise medium -> `review-required`; otherwise -> `no-static-blocker`.

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

Before changing this package, preserve an immutable baseline and exact source snapshot for material research/evidence bytes. Freeze evaluator inputs before candidate mutation and record evaluator hashes. Compare baseline vs candidate with the same frozen evaluator where compatible. Keep structural, behavioral, runtime, and semantic-review evidence separate.

Package only the exact frozen candidate after all applicable validators pass; bind the archive to a durable hash/receipt. Any post-pass edit invalidates affected evidence and requires revalidation. Keep packaging host-neutral.
