---
name: migration-conflict-analyzer
description: Analyze EF Core migration files and diffs for reproducible conflict, ordering, destructive-change, snapshot, raw-SQL, and deployment hazards with exact input identity, stable findings, bounded heuristics, and machine-readable receipts.
---

# Migration Conflict Analyzer

## Purpose

Analyze Entity Framework Core migration files, diffs, and pull-request migration changes for schema conflicts, ordering hazards, data-loss signals, snapshot divergence, raw-SQL risks, and runtime migration deployment hazards.

Use the installed analyzer as an evidence-producing static analysis tool. Prefer exact migration bytes, immutable Git revision identity, generated SQL when supplied, and explicit deployment evidence over assumptions.

Do not use this skill for generic EF Core tutorials, normal database design, or ordinary application-code review unless migration conflict/risk analysis is the requested task.

## Reproducibility contract

This skill is a `research-analytic` workflow with deterministic mechanics and bounded heuristic judgment.

Mechanically reproducible surfaces:

- input file SHA-256 identities;
- resolved Git base/head/merge-base identities in PR mode;
- ModelSnapshot and generated-SQL identities when supplied/discovered;
- canonical migration ordering and operation extraction;
- versioned heuristic-set identity and hash;
- stable rule IDs, finding IDs, severity, gate, and confidence fields;
- machine-readable report and analysis receipt;
- same-input rerun identity for supported static inputs.

Judgment that remains bounded rather than deterministic:

- whether drop/add represents an intended rename;
- whether destructive operations actually lose required data;
- provider-specific SQL/locking/transaction behavior;
- whether raw SQL is semantically safe beyond recognized patterns;
- whether rolling deployment topology creates an actual runtime failure.

Never convert those unknowns into certainty. Findings must preserve `confidence`, `evidence_status`, and `uncertainty`.

The frozen heuristic contract is `references/heuristic-set.json`. The current contract version is `2.0.0`. Do not silently reinterpret a rule ID, severity, or gate. Incompatible heuristic changes require a version change plus regression re-baseline.

## Modes

Choose exactly one primary mode:

1. **file/directory mode** — one or more migration files/directories are available.
2. **PR/Git mode** — a repository plus base ref/commit is available.
3. **manual review mode** — only pasted snippets or incomplete evidence are available; apply the same taxonomy manually and label script gates `not-run`.

PR/Git mode is preferred when the question is about branch conflicts because it binds analysis to exact base/head identities and can compare changed migration identities with base history.

## Deterministic analyzer

### File/directory mode

```bash
python3 -S scripts/migration_conflict_analyzer.py <paths> \
  --format json \
  --output migration-conflict-report.json \
  --receipt migration-conflict-analysis-receipt.json
```

Include supporting snapshots found under directory inputs when relevant:

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --include-support-files \
  --format json
```

### PR/Git mode

```bash
python3 -S scripts/migration_conflict_analyzer.py . \
  --git-base origin/main \
  --format json \
  --output migration-conflict-report.json \
  --receipt migration-conflict-analysis-receipt.json
```

The report must record:

- requested Git base;
- resolved base SHA;
- HEAD SHA;
- merge-base SHA;
- changed-file identities;
- changed migration hashes;
- relevant snapshot identities;
- base migration-history identities used for collision checks.

Do not call working-tree bytes immutable Git evidence. File hashes are the identity of analyzed working bytes; Git SHAs identify repository revisions.

### Optional evidence

Bind generated SQL without claiming it was executed:

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --generated-sql migration.sql \
  --format json
```

Supply runtime migration code only when runtime deployment analysis is requested:

```bash
python3 -S scripts/migration_conflict_analyzer.py <path> \
  --runtime-code Program.cs \
  --deployment-instances multiple \
  --format json
```

A runtime concurrency finding requires explicit startup-migration code evidence plus supplied `multiple` deployment-instance evidence. Without that evidence, do not claim a concurrent runtime failure.

## Analysis order

1. Resolve input mode and exact scope.
2. Capture migration/support/runtime/generated-SQL file hashes.
3. In Git mode, resolve immutable base/head/merge-base identities before interpreting conflicts.
4. Parse main migration `Up`/`Down` operations into canonical operation records.
5. Sort `Up` operations by migration timestamp/file order, then source invocation order.
6. Load `references/heuristic-set.json`; record version and SHA-256.
7. Apply only the frozen rule taxonomy.
8. Emit stable finding IDs from rule ID + canonical operation/evidence subjects.
9. Separate observed/derived evidence from inferred intent.
10. Emit gates, summary, explicit limitations, and `analysis_receipt`.
11. If writing artifacts, use output-path preflight and preserve last-good outputs on commit failure.

## Required risk coverage

Load `references/conflict-heuristics.md` when explaining findings. Coverage includes:

- duplicate AddColumn/CreateTable/named-object operations;
- conflicting index definitions;
- conflicting foreign-key definitions;
- DropColumn/DropTable destructive-operation review gates;
- rename vs drop/add heuristic with explicit uncertainty;
- ordering after drop/rename;
- required-column additions without default/backfill evidence;
- branch/base migration-history collisions;
- ModelSnapshot divergence signals;
- raw SQL mutation, narrow non-idempotency patterns, and transaction suppression;
- runtime startup-migration hazards only from supplied evidence;
- unknown/custom migrationBuilder operations as manual-review coverage gaps;
- expand/backfill/contract sequence detection as a low-confidence pattern, never proof of safe rolling compatibility.

## Stable severity and gate rules

Severity and gate come from `references/heuristic-set.json`, not free-form reviewer judgment.

- `critical` / `block`: deterministic identity/schema conflicts that should not be merged/applied without resolution.
- `high` / `review-required`: destructive operations or strong deployment/order hazards needing explicit remediation/evidence.
- `medium` / `review-required`: plausible integration/upgrade hazards whose actual impact depends on data/provider/context.
- `low` / `manual-review`: coverage gaps or review signals that are not themselves merge blockers.
- `info` / `none`: non-blocking structural observations when present.

Do not promote severity because a finding sounds alarming. Do not downgrade it to make a candidate pass. Change the versioned heuristic contract only through an explicit re-baseline.

## Evidence and confidence

Every finding must include:

- stable `id`;
- stable `rule_id`;
- `severity`;
- `confidence`;
- `evidence_status`;
- `gate`;
- `hazard_type`;
- exact files/operation IDs or supporting evidence identity;
- why it matters;
- smallest safe remediation;
- validation step;
- explicit `uncertainty`.

Use these evidence meanings:

- `observed`: directly present in analyzed bytes/options;
- `derived`: deterministic calculation from observed evidence;
- `inferred`: bounded heuristic interpretation;
- `supplied`: contextual evidence explicitly supplied by the user/tooling;
- `blocked`: semantics cannot be established by the analyzer.

## ModelSnapshot handling

ModelSnapshot is supporting evidence, not a replacement for migration operations.

In Git mode:

- record changed snapshot identity;
- record base snapshot identity when available;
- flag snapshot-only changes as divergence signals;
- flag changed migrations without a changed snapshot only as a review signal, because some legitimate migrations may not alter snapshot state;
- never claim future migration corruption from snapshot divergence alone.

## Raw SQL handling

Raw SQL is intentionally bounded:

- hash/bind the migration file containing it;
- identify schema/data mutation keywords;
- identify only narrow rerun-sensitive patterns such as self-increment or unguarded insert;
- detect `suppressTransaction: true` when present;
- keep confidence and uncertainty explicit;
- require generated/provider-specific SQL execution for runtime conclusions.

Do not claim a raw SQL statement is safe merely because no rule matched.

## Runtime deployment hazard taxonomy

Runtime findings describe evidence-backed hazard classes, not predicted failures:

- `runtime-deployment`: application startup applies migrations;
- `runtime-concurrency`: startup migration plus explicit multi-instance deployment evidence;
- `transaction`: raw SQL intentionally bypasses the migration transaction;
- `data-migration`: rerun-sensitive data mutation pattern;
- `ordering`: later migration operations depend on objects already dropped/renamed;
- `destructive-schema`: contract step removes schema objects.

Prefer migration bundles/scripts or a single deployment migration job when runtime startup application is a relevant risk, but tie the recommendation to the observed deployment evidence.

## Output contract

The output contract is defined by `references/report-contract.md`; JSON is the canonical machine-readable form.


Use `references/report-contract.md` for prose and machine-readable output requirements. JSON output must conform to the semantic contract documented by `schemas/analysis-report.schema.json`.

A `no-static-blocker` result means only that the frozen static heuristic set emitted no blocking/high/medium finding for the supplied evidence. It is not a production-safety guarantee.

## Validation and frozen scenarios

Package-owned validation:

```bash
python3 -S scripts/validate_contracts.py --skill-root .
```

Executable regression suite:

```bash
python3 -S evals/run_analyzer_regressions.py \
  --analyzer scripts/migration_conflict_analyzer.py \
  --scenarios evals/analyzer-regression-scenarios.json \
  --expected-heuristics evals/expected-heuristics.json
```

The frozen regression contract covers:

- duplicate AddColumn;
- DropColumn;
- rename vs drop/add;
- conflicting indexes;
- conflicting FKs;
- migration ordering;
- branch divergence/base collision;
- snapshot divergence;
- raw SQL;
- non-idempotent data migration;
- concurrent deploy hazard;
- harmless migration;
- unknown operation;
- same-diff rerun stability.

Do not edit frozen expected outcomes to make analyzer changes pass. A legitimate evaluator correction requires a new baseline/freeze before accepting analyzer behavior.


## Release and evaluator freeze discipline

When this skill package itself is changed, preserve an immutable baseline/source snapshot of the exact prior bytes before mutation. Freeze evaluator inputs and expected outcomes before evaluating the candidate; do not edit frozen evaluator assets to make a candidate pass.

Compare baseline vs candidate with the same frozen regression inputs before making a behavioral-improvement claim. After the final pass, freeze the candidate and do not make unvalidated edits; any post-pass change restarts the affected validation gates.

Keep evidence layers separate:

- **structural evidence**: package shape, schema/contract validity, hashes;
- **behavioral evidence**: executed regression scenarios and stable rerun identities;
- **runtime evidence**: actual provider/database/deployment execution;
- **perceptual evidence**: not applicable to this analyzer.

The target package does not need to own its own archive builder. Packaging may be performed by the host/meta-skill, but the package must represent the exact frozen candidate and include a package receipt that binds the delivered archive to that candidate.

## PR workflow

Load `references/pr-workflow.md` for collection and review sequencing. Base conflict claims require the base migration history to have been inspected from the resolved base SHA.

## Stop conditions

Stop or return a bounded partial analysis when:

- no migration/diff/snapshot evidence is available;
- PR mode is requested but the repository/base revision cannot be resolved;
- custom helper methods hide material migration behavior and no generated SQL is available;
- a runtime safety conclusion is requested without deployment topology/provider/generated SQL/data evidence needed for that conclusion;
- heuristic/evaluator identity cannot be established;
- output aliases an analyzed input, evaluator, or receipt path;
- the only way to produce a passing result is to weaken a frozen severity/gate/evaluator.
