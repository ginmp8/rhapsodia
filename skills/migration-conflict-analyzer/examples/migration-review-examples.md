# Migration Conflict Analyzer Examples

These examples show the distinction between observed evidence and bounded interpretation. Rule IDs and severities come from `references/heuristic-set.json`.

## Duplicate AddColumn

Two changed migrations both add `Customers.Email`.

Expected primary finding:

- rule: `duplicate.add-column`;
- severity: critical;
- evidence status: derived;
- gate: block;
- rationale: duplicate structured creation is directly derived from the changed operations.

## Standalone DropColumn

A migration drops `Customers.LegacyCode`.

Expected primary finding:

- rule: `destructive.drop-column`;
- severity: high;
- evidence status: observed;
- uncertainty: data presence and consumer dependency are unknown.

Do not rewrite this as "data loss will occur" without data/consumer evidence.

## Drop/Add possible rename

One migration drops `Customers.Name` and adds `Customers.FullName`.

Expected findings include destructive review plus `rename.drop-add`. The rename interpretation is inferred/medium-confidence because replacement can be intentional.

## Conflicting indexes

Two migrations create indexes over the same table/column set but disagree on uniqueness or identity.

Expected primary finding: `conflict.index-definition` high. Multiple same-column indexes can be intentional, so the report requests reconciliation rather than asserting invalid SQL.

## Conflicting FKs

Two migrations map `Orders.OwnerId` to different principal tables.

Expected primary finding: `conflict.foreign-key-definition` high with explicit business-intent uncertainty.

## Raw SQL increment

`UPDATE Counters SET Value = Value + 1` inside `migrationBuilder.Sql(...)`.

Expected findings include:

- `raw-sql.opaque-mutation`;
- `raw-sql.non-idempotent-data`.

The second rule detects a narrow rerun-sensitive pattern. Provider behavior and surrounding guards still require exact SQL execution evidence.

## Runtime startup migration

Runtime code contains `Database.MigrateAsync()` and deployment evidence explicitly says multiple application instances can start.

Expected primary finding: `runtime.concurrent-startup-migrate` high. Report a concurrency hazard, not a guaranteed failure.

## Harmless static case

A single migration adds one nullable column to an existing table, with no other evidence.

Expected: no critical/high/medium finding from the frozen static heuristic set. This means `no-static-blocker`, not "production safe".
