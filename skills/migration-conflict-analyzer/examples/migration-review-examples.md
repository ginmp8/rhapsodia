# Example Migration Review Cases

## Duplicate column across PR migrations

Input signal:

- `20260401090000_AddCustomerEmail.cs`: `AddColumn("Email", table: "Customers")`
- `20260401103000_AddEmailToCustomer.cs`: `AddColumn("Email", table: "Customers")`

Expected finding: critical duplicate column creation.

## Safe disjoint column additions with runtime warning

Input signal:

- migration A adds `Customers.Email`;
- migration B adds `Customers.Phone`;
- application applies migrations during startup.

Expected finding: no deterministic schema conflict, but medium runtime deployment hazard if multiple instances apply migrations concurrently or app starts using columns before migration completes.

## Unsafe rename

Input signal:

- migration drops `Customers.Name` and adds `Customers.FullName`.

Expected finding: high data-loss risk; recommend `RenameColumn` or explicit backfill.

## Not-null column on existing table

Input signal:

- `AddColumn(nullable: false)` without `defaultValue`, `defaultValueSql`, or computed column;
- table is not created in the same PR.

Expected finding: high risk for populated database.

## Raw SQL backfill dependency

Input signal:

- raw SQL updates `Customers.Email`;
- another migration adds `Customers.Email`.

Expected finding: medium or high ordering risk depending on operation order and same migration grouping.
