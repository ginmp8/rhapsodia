# EF Core Migration Conflict Heuristics v2

The machine authority for rule IDs, severity, confidence defaults, gates, and hazard types is `heuristic-set.json` version `2.0.0`. This document explains intent and limits; it must not override the JSON contract.

## Evidence classes

- **Observed**: operation/text/flag exists in analyzed bytes.
- **Derived**: deterministic relation between observed identities or ordered operations.
- **Inferred**: intent/impact is a bounded heuristic.
- **Supplied**: deployment/provider context was explicitly supplied.
- **Blocked**: the analyzer cannot determine semantics.

A heuristic finding is not runtime proof. Keep the finding's confidence and uncertainty text in final reporting.

## Deterministic identity/schema conflicts

Critical/blocking rules include duplicate column/table/object creation and collisions between changed migration identity and the resolved Git base history.

Typical remediation:

- rebase on current migration history;
- regenerate the newer migration from the reconciled model/snapshot;
- keep one creation operation;
- avoid rewriting migrations already applied in shared environments.

## Destructive operations

`DropColumn` and `DropTable` trigger high destructive-review findings because the source operation is objectively destructive. The analyzer does **not** infer that required data exists or that consumers still use the object.

Validate:

- consumer compatibility;
- data retention/backups;
- generated SQL;
- representative upgrade path;
- staged expand/contract when old/new application versions can coexist.

## Rename vs drop/add

Drop plus add on one table can represent:

- an unsafe scaffolded rename;
- an intentional replacement;
- two unrelated schema changes.

Therefore `rename.drop-add` is intentionally an inferred, medium-confidence interpretation even though its stable severity is high. Prefer `RenameColumn` when identity is preserved; otherwise make copy/backfill/drop sequencing explicit.

## Ordering hazards

The analyzer derives operation order from migration timestamp/file ordering and source invocation order within `Up()`.

Flag when:

- a later structured operation references a column/table already dropped;
- a later operation still references the old name after `RenameColumn`.

Generated SQL remains the final provider-specific ordering evidence.

## Conflicting indexes and FKs

Index conflict compares the same table/column set with different index identity/uniqueness definitions. Multiple indexes over the same columns can be intentional, so the finding requests review rather than asserting invalidity.

Foreign-key conflict compares the same local table/column set with different principal targets. Transitional relationships can be intentional; business intent is not inferred.

## Required columns and unique indexes

A required `AddColumn(nullable: false)` without default/computed/backfill evidence is a high upgrade risk on an existing table, but the analyzer does not know existing row count or prior operational backfills.

Unique index creation is a medium data-compatibility signal because existing duplicates are unknown until data is inspected.

## ModelSnapshot divergence

Snapshot signals include:

- changed snapshot without changed migration;
- in Git mode, changed migration without changed snapshot.

These are review signals. They do not by themselves prove migration failure or future snapshot corruption.

## Raw SQL

Raw SQL rules intentionally use a narrow vocabulary:

- schema/data mutation keywords -> opaque-mutation review;
- self-increment/self-decrement and unguarded insert patterns -> rerun-sensitive/non-idempotent signal;
- `suppressTransaction: true` -> transaction hazard;
- otherwise -> manual review.

No regex result substitutes for executing the exact provider-specific SQL.

## Runtime migration hazards

A startup migration finding requires explicit code evidence such as `Database.Migrate()`/`MigrateAsync()` from files supplied via `--runtime-code`.

The stronger concurrent-startup rule additionally requires `--deployment-instances multiple`. Even then, report a **hazard**, not a guaranteed failure; provider locking, EF behavior, orchestration, and timing remain external evidence.

## Expand/contract detection

The analyzer may emit a low-confidence pattern when it observes an add -> raw SQL/backfill -> drop sequence on one table. This only says the sequence resembles expand/backfill/contract. It does not prove semantic column mapping, consumer compatibility, or safe rolling deployment.

## Unknown operations

Unknown/custom `migrationBuilder` operations are coverage gaps. The correct behavior is `manual-review` with blocked semantics, not invented behavior. If the operation recurs, add a versioned parser rule and regression scenario before relying on automated classification.
