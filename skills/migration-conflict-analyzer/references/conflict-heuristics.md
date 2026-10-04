# EF Core Migration Conflict Heuristics v3

Machine authority for rule IDs, severity, confidence defaults, gates, and hazard types is `heuristic-set.json` version `3.0.0`. This file explains interpretation only; it never overrides the JSON contract.

## Evidence classes

- **observed** — present directly in analyzed bytes/options.
- **derived** — deterministic relation between observed identities/operations.
- **inferred** — bounded intent/impact interpretation.
- **supplied** — explicit semantic/deployment context supplied to the analyzer.
- **blocked** — semantics cannot be established safely.

## Identity, lineage, and scope

Use the full migration ID (`yyyyMMddHHmmss_Name`) as migration identity. A shared 14-digit timestamp is only a low-confidence parallel-authoring signal; it is not a deterministic conflict by itself.

Scope migration identity by the best available migration-set evidence: DbContext and migrations assembly when supplied/derived, otherwise directory scope. In Git mode compare changed migration identity and bytes with the resolved base history.

When a ModelSnapshot actually exposes `LastMigrationId`, compare it with the latest observed migration in the same set and use `history.diverged-lineage` for deterministic mismatch. Do not infer EF11 snapshot capabilities from a version string when the identity is absent.

## Destructive changes and rollback

`DropColumn` and `DropTable` remain high review gates because the operation is objectively destructive. The analyzer does not infer that important rows/consumers exist.

If `Down` merely recreates a dropped column/table, `rollback.data-not-restorable` records that structural inversion does not reconstruct original data. External backups/custom SQL can change recoverability and remain outside static proof.

A `Down` that explicitly throws `NotSupportedException` is reported as an informational structural observation rather than being treated as safer or worse than a fabricated inverse.

## Structured data operations

`InsertData`, `UpdateData`, and `DeleteData` are first-class data mutations. Review key targeting, rerun behavior, provider-generated SQL, and rollback strategy. Do not restrict data-migration analysis to raw SQL.

## Column and constraint compatibility

Flag these as data-compatibility review surfaces:

- required `AddColumn` without default/backfill evidence;
- nullable -> non-nullable `AlterColumn`;
- reduced maximum length;
- reduced precision/scale;
- provider store-type change;
- new unique/check/primary-key constraints or unique indexes over existing data.

No static rule claims existing rows violate the new contract; validate actual data separately.

## Raw SQL and transaction boundaries

Raw SQL classification stays intentionally narrow: mutation vocabulary, rerun-sensitive insert/self-update patterns, and `suppressTransaction: true`. Absence of a match never proves safety.

Optional semantic evidence may report provider-generated transaction-suppressed commands. Keep this separate from static source flags and bind the semantic-evidence file hash.

## Runtime migration classification

`Database.Migrate`/`MigrateAsync` is a runtime-deployment review signal.

For explicit multiple-instance evidence:

- EF major unknown -> `runtime.concurrent-startup-version-unknown`;
- EF < 9 -> `runtime.concurrent-startup-unprotected`;
- EF >= 9 -> `runtime.concurrent-startup-lock-aware`.

The EF9+ rule deliberately stays a review finding: migration locks coordinate migration executors but do not prove old/new application compatibility, provider-specific failure behavior, or safe DDL overlap.

For EF9+ runtime source that also contains an explicit transaction pattern around migration execution, emit `runtime.explicit-migrate-transaction` as an inferred review hazard and require exact runtime-path validation.

## Provider profiles

Provider facts are versioned in `provider-profiles.json`.

- **SQL Server**: EF9+ migration locking is provider-backed; generated index SQL without observed `ONLINE = ON` is an operational-locking signal, not an outage prediction.
- **PostgreSQL/Npgsql**: provider migration locking is explicit; generated `CREATE INDEX` without `CONCURRENTLY` is an operational-locking signal.
- **SQLite**: selected operations use table rebuild semantics; EF idempotent migration script generation is unsupported; EF9+ locking uses the provider lock mechanism and can require abandoned-lock recovery.

Unknown providers receive only generic rules. Never copy a known provider's behavior to an unknown provider.

## Provider branching and nondeterminism

Provider-specific migration code using `ActiveProvider` is valid, but incomplete branching is a review hazard when the analyzed migration contains provider-sensitive code with no explicit unsupported-provider path.

Runtime-dependent values/calls (`DateTime.Now/UtcNow`, `Guid.NewGuid`, environment, filesystem, network) are determinism review signals. They do not automatically prove nondeterministic SQL, but historical migration behavior should not silently vary with execution environment.

## SQL artifact integrity

Hash generated, reviewed, deployment, and rollback SQL separately.

- reviewed != deployment bytes -> `artifact.review-execution-drift` (`critical/block`);
- generated != reviewed bytes -> review-required drift signal.

These are identity findings, not semantic comparisons. Different bytes can be better or worse; the analyzer only proves the claimed review/execution identity is broken.

## Optional semantic evidence

`schemas/semantic-evidence.schema.json` allows host-neutral evidence such as EF version/provider/context, pending-model-changes state, migration-lock status, and transaction-suppressed command count.

The Python core never requires .NET. A host that can build/run EF tooling may produce the semantic-evidence JSON separately; a host without that capability still runs the full portable static core.

## Unknown/custom operations

Unknown `migrationBuilder` operations remain `manual-review` coverage gaps. Do not guess semantics. Repeated custom/provider operations should gain a versioned parser rule and frozen regression before automated classification is trusted.
