# PR Migration Review Workflow

## Inputs

Prefer these inputs, in order:

1. changed migration files from the PR;
2. changed `ModelSnapshot` and `*.Designer.cs` files as supporting signals;
3. base-branch migration files for duplicate history comparison;
4. generated SQL script from the PR branch;
5. provider, DbContext name, and deployment model.

## Local repository workflow

From the repository root:

```bash
python3 -S scripts/migration_conflict_analyzer.py . --git-base origin/main --format markdown --output migration-conflict-report.md
```

The script asks Git for changed files and analyzes changed migration main files, excluding `*.Designer.cs` and `*ModelSnapshot.cs` from operation parsing. It still records snapshot/designer changes as review signals when present in the diff.

If Git is unavailable, pass files or folders directly:

```bash
python3 -S scripts/migration_conflict_analyzer.py path/to/Migrations --format markdown
```

## Connector workflow

When a PR is only available through a connector:

1. fetch the PR file list or diff;
2. identify added/modified migration main files;
3. read each changed migration file;
4. read changed snapshot/designer files only for divergence signals;
5. if the analyzer cannot run, apply `references/conflict-heuristics.md` manually and clearly state that deterministic parsing was not executed.

## Review comment shape

For each blocking finding, write:

- file and operation;
- why this can fail or lose data;
- smallest concrete fix;
- validation command to run before merge.

Example:

```markdown
High: `AddColumn(nullable: false)` adds `Customers.Email` without default/backfill on an existing table. This can fail on populated databases. Make the column nullable first or add a controlled default/backfill, then enforce NOT NULL in a later migration. Validate with `dotnet ef migrations script --idempotent`.
```

## Merge decision

- Block merge for critical findings.
- Request changes for high findings unless the team provides generated SQL plus a production-safe deployment plan.
- Allow merge with notes for medium findings when generated SQL is reviewed and deployment sequencing is safe.
