---
name: migration-conflict-analyzer
description: use when asked to analyze entity framework core dotnet migration files or pull request migration changes for schema conflicts, ordering hazards, data-loss risks, duplicate operations, runtime migration deployment hazards, model snapshot divergence signals, raw sql risks, and expand-contract compatibility issues. use for uploaded migration .cs files, repository paths, git diffs, pull requests, or pasted migration code. do not use for generic ef core tutorials, normal database design, or application code review unless migration conflict analysis is requested.
---

# Migration Conflict Analyzer

## Purpose

Analyze Entity Framework Core migration files for conflicts and deployment hazards before they are merged or applied. Prefer evidence from migration source files, diffs, generated SQL, repository context, and official EF Core guidance over assumptions.

## Core workflow

1. Determine the mode:
   - **file mode**: user provides one or more migration `.cs` files, pasted code, or a local path.
   - **pr mode**: user asks to analyze all migrations in a pull request, branch, or diff.
   - **review mode**: user wants reasoning about a specific flagged migration or conflict.
2. Gather migration inputs.
   - For uploaded files, use the uploaded files directly.
   - For repository paths or PRs, inspect changed migration files. Exclude `*.Designer.cs` and `*ModelSnapshot.cs` from operation analysis unless snapshot divergence is part of the request.
   - When connectors are available for PRs, use the GitHub/Drive/search tools to fetch changed files or diffs. If local repository access exists, prefer the script's `--git-base` mode.
3. Run deterministic analysis when files are available:
   ```bash
   python3 -S scripts/migration_conflict_analyzer.py <paths> --format markdown --output migration-conflict-report.md
   ```
   For local PR analysis:
   ```bash
   python3 -S scripts/migration_conflict_analyzer.py . --git-base origin/main --format markdown --output migration-conflict-report.md
   ```
4. Load `references/conflict-heuristics.md` when explaining findings, severity, or coverage.
5. Load `references/pr-workflow.md` for PR-specific collection, base-branch comparison, and review comments.
6. Use `references/report-contract.md` for the final report shape.

## What to flag

Flag both deterministic conflicts and operational risks. Important categories include:

- duplicate `AddColumn`, `CreateTable`, `CreateIndex`, constraint, or foreign-key names across migrations in the same PR;
- one migration dropping or renaming a table or column while another migration touches the same object;
- multiple migrations altering the same table or column in ways that depend on order;
- `DropColumn` plus `AddColumn` patterns that look like unsafe renames;
- `NOT NULL` column additions to existing tables without default, computed value, or explicit backfill;
- raw `migrationBuilder.Sql(...)` statements that perform DDL, mutate data, depend on newly added columns, or are not obviously idempotent;
- divergent migration history signals such as duplicate timestamps, duplicate class names, deleted migrations, edited old migrations, or snapshot changes that do not correspond to changed migrations;
- runtime application of migrations hazards, especially when the app calls `Database.Migrate()` or `MigrateAsync()` during startup and multiple instances may start concurrently.

## Severity rules

Use this default severity model unless the user supplies team-specific rules:

- **Critical**: likely to fail migration execution or corrupt migration history, e.g. duplicate migration identifiers, duplicate object creation, drop/rename combined with dependent operations, or conflicting table recreation.
- **High**: likely data loss, deployment failure on populated databases, or unsafe ordering, e.g. non-null column without default/backfill on an existing table, raw destructive SQL, unsafe rename generated as drop/add.
- **Medium**: plausible production or PR integration risk, e.g. multiple migrations touch the same table, multiple `AlterColumn` operations on one column, opaque raw SQL, snapshot divergence signals.
- **Low**: review attention or maintainability issue, e.g. naming inconsistencies, empty `Down()`, missing explicit recommendation, or operations that are safe but should be validated with generated SQL.

## Output contract

Return a concise but complete report:

1. Scope analyzed: files, PR/diff source, base branch if any, and excluded files.
2. Executive summary: count by severity and whether merge/apply is blocked.
3. Findings: severity, migration file, operation evidence, why it can conflict, and smallest safe fix.
4. Safe deployment guidance: use scripts/bundles or a single migration job instead of every app instance applying migrations at startup when relevant.
5. Validation performed: script command, parsing limits, generated report path, and checks not executed.
6. Residual risks: provider-specific behavior, data volume, lock duration, and raw SQL not fully interpreted.

## Handling PR mode

For PR review, compare only files changed in the PR when possible, then optionally compare against existing base migrations to detect duplicate timestamps, duplicate class names, or object additions already present in base. Do not claim a base conflict unless base files were inspected.

If the PR includes `*ModelSnapshot.cs`, inspect it as a signal but do not rely only on it. Migrations include both operations and a snapshot, so snapshot divergence can corrupt future migrations even when current migrations apply.

## Script notes

The bundled analyzer is intentionally conservative. It uses regex and brace matching, not a full C# compiler. Treat script findings as evidence-backed heuristics and use human review for provider-specific SQL, custom helpers, conditional code, or unusual formatting.

## Stop conditions

Stop or report a partial result when:

- no migration files or diffs are available;
- PR mode is requested but the changed migration files cannot be retrieved;
- a repository uses custom migration helpers that the script cannot parse and no generated SQL is available;
- the user asks for certainty about production safety without database provider, current schema, data volume, and generated SQL.
