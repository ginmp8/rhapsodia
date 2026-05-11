# EF Core Migration Conflict Heuristics

## Table of contents

1. Deterministic conflicts
2. Ordering and dependency hazards
3. Data-loss and data-volume hazards
4. PR and team-history hazards
5. Runtime migration hazards
6. Raw SQL hazards
7. Provider-specific considerations
8. Recommended fixes

## 1. Deterministic conflicts

Flag as critical or high when two or more changed migrations try to create the same database object:

- same table via `CreateTable`;
- same column via `AddColumn` on the same table;
- same index name via `CreateIndex`;
- same foreign key, primary key, unique constraint, check constraint, or default constraint name;
- same migration timestamp, class name, or migration id.

Why it matters: the second migration usually fails because the object already exists, or it leaves migration history inconsistent if one migration was partially applied manually.

Preferred fixes:

- consolidate compatible column additions into one migration when they belong to the same model change;
- regenerate one branch's migration after rebasing on the latest migration and snapshot;
- use unique explicit names for indexes and constraints;
- do not edit previously applied migrations except under a controlled reset/squash process.

## 2. Ordering and dependency hazards

Flag when one migration changes object identity while another migration references the old identity:

- `RenameColumn` plus `AddColumn`, `DropColumn`, `AlterColumn`, `CreateIndex`, or raw SQL on the old or new column;
- `RenameTable` plus operations on the old or new table;
- `DropColumn` or `DropTable` before another migration uses that object;
- `AlterColumn` repeated on the same column in separate migrations in the same PR;
- `CreateTable` followed by `DropTable` for the same table in the same PR.

Preferred fixes:

- place dependent changes in the same migration when the order is inseparable;
- replace unsafe drop/add rename patterns with `RenameColumn` or `RenameTable`;
- split destructive changes into expand-contract releases.

## 3. Data-loss and data-volume hazards

Flag as high when a migration can fail or lose data in a populated database:

- `DropColumn`, `DropTable`, destructive raw SQL, or `AlterColumn` that narrows type/length/nullability;
- `AddColumn(nullable: false)` to an existing table without `defaultValue`, `defaultValueSql`, computed column, or preceding backfill;
- table rewrite operations that can lock large tables;
- adding unique indexes before deduplicating existing rows;
- required foreign keys added before existing data is cleaned.

Preferred fixes:

- add nullable columns first, backfill, then enforce `NOT NULL` later;
- add defaults intentionally and remove them later only when safe;
- validate generated SQL and run it against a production-like copy;
- split large backfills into operational jobs instead of a blocking migration.

## 4. PR and team-history hazards

EF Core migrations are not just SQL scripts; they also include the model snapshot at the time the migration was generated. In team environments, concurrent branch migrations can produce divergent snapshots.

Signals to flag:

- multiple newly generated migrations from different branches touching the same `DbContext`;
- `ModelSnapshot` changed without corresponding migration changes;
- migrations changed without a snapshot change, unless intentionally editing an old migration before application;
- deleted or renamed migration files in a PR;
- duplicate or out-of-order timestamps;
- changed `*.Designer.cs` without matching main migration file.

Preferred fixes:

- rebase on the branch containing the latest migration;
- remove and regenerate the newer branch migration with the current snapshot;
- run `dotnet ef migrations has-pending-model-changes` where available;
- generate and inspect an idempotent SQL script before merge.

## 5. Runtime migration hazards

Running migrations automatically from normal application startup can be risky when multiple app instances start or deploy concurrently.

Flag as medium or high in migration reports when the user mentions runtime migration problems or repository code contains startup `Database.Migrate()`/`MigrateAsync()` patterns.

Preferred deployment model:

- generate SQL scripts or migration bundles in CI/CD;
- run migrations once as a deploy step, Kubernetes Job, release task, or DBA-reviewed change;
- then roll out the application;
- prefer expand-contract migrations so old and new app versions can coexist during rolling deploys.

## 6. Raw SQL hazards

Raw SQL is opaque to static analysis. Flag `migrationBuilder.Sql(...)` when it contains:

- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `UPDATE`, `DELETE`, `MERGE`, `EXEC`, `CREATE INDEX`, or provider-specific DDL;
- object names touched by other migrations in the same PR;
- non-idempotent object creation;
- data backfill that assumes new columns already exist;
- `suppressTransaction: true`.

Preferred fixes:

- document the dependency and expected order in the migration comment;
- make object creation idempotent where the provider supports it;
- keep raw SQL close to the schema operation it depends on;
- test generated SQL against a clean database and an upgraded database.

## 7. Provider-specific considerations

Do not overclaim without knowing the provider. SQL Server, PostgreSQL, SQLite, MySQL, and Oracle differ in:

- type names and column defaults;
- transactional DDL behavior;
- lock granularity and duration;
- identifier casing and schema handling;
- online index capabilities;
- whether `IF EXISTS` or `IF NOT EXISTS` is available.

## 8. Recommended fixes by finding type

- duplicate add column: delete/regenerate one migration or merge operations into one migration;
- unsafe rename: use `RenameColumn`/`RenameTable` and preserve data;
- not-null add: add nullable or default/backfill before making required;
- repeated alter: consolidate or make order explicit;
- destructive operation: split into expand-contract and verify consumers no longer depend on the object;
- raw SQL: add comments, idempotency, generated SQL review, and database-specific tests;
- snapshot divergence: regenerate the migration from the updated branch.
