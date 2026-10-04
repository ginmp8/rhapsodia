# Migration Review Examples v3

## Parallel branches with the same timestamp

Two files named `20261004103000_AddFoo.cs` and `20261004103000_AddBar.cs` share a timestamp but have different full migration IDs. Report `history.duplicate-timestamp` as a low/manual-review signal, not a blocker. If the full migration ID collides with different bytes or lineage diverges from the reconciled history, use the blocking identity/lineage rule instead.

## EF8 vs EF10 startup migration

`Database.MigrateAsync()` plus `--deployment-instances multiple` is version-sensitive. EF8 maps to the pre-lock high review rule. EF10 maps to the lock-aware medium review rule, while still requiring provider/deployment validation. Unknown EF version remains explicitly uncertain.

## Rollback that recreates a dropped column

`Up` drops `Customers.Cpf`; `Down` adds `Customers.Cpf`. Report the destructive operation and `rollback.data-not-restorable`: recreating the column does not reconstruct prior CPF values.

## Structured data migration

`InsertData`, `UpdateData`, and `DeleteData` are provider-aware data changes even without `migrationBuilder.Sql`. Report them as structured data mutations and review keys, rerun behavior, generated SQL, and rollback.

## Reviewed SQL drift

If `reviewed.sql` and `deployment.sql` hash differently, emit `artifact.review-execution-drift` and block the claimed review-to-execution chain. Do not claim the deployment SQL is unsafe solely because bytes differ.

## Optional semantic evidence

A separate EF-aware probe can write:

```json
{
  "schema_version": "1.0",
  "ef_core_version": "10.0.0",
  "provider": "Microsoft.EntityFrameworkCore.SqlServer",
  "dbcontext": "AppDbContext",
  "pending_model_changes": false,
  "transaction_suppressed_command_count": 0
}
```

The analyzer hashes this file and treats its values as `supplied` evidence. The static core remains usable without this file or the .NET SDK.
