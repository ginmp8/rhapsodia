# Dependency Tracing Guide

Use this file when searching a repository to build or verify a context map.

## General search sequence

1. Search exact symbols and file names.
2. Search callers and usages.
3. Search registrations and configuration.
4. Search tests and fixtures.
5. Search similar implementations.
6. Search docs, migration notes, generated code instructions, and CI commands.

## Useful local commands

Prefer repository-native tools when available. If shell access exists, use combinations like:

```bash
rg "SymbolName|config_key|endpoint|error message" .
rg "class SymbolName|interface SymbolName|def symbol_name|function symbolName" .
rg "SymbolName" --glob '*test*' --glob '*spec*'
git grep "SymbolName"
git ls-files | rg "name|domain|feature"
```

## Trace dimensions

- **Imports/exports**: modules that import the changed file, barrel exports, public API surfaces.
- **Type references**: interfaces, base classes, generics, DTOs, schemas, validators, serialization contracts.
- **Runtime wiring**: dependency injection, routers, handlers, consumers, background jobs, schedulers, feature flags.
- **Data boundaries**: migrations, ORM mappings, query projections, indexes, seed data, generated clients.
- **Operational hooks**: metrics, logs, traces, alerts, dashboards, retries, idempotency, locks, rate limits.
- **Tests**: unit, integration, contract, snapshot, fixture, golden file, migration, smoke, and e2e tests.

## Ecosystem hints

### .NET / C#

Search for interfaces, handlers, DI registrations, options classes, hosted services, EF mappings, migrations, MediatR handlers, validators, and test fixtures. Watch for extension methods and source generators.

### Python

Search imports, FastAPI routers, Pydantic models, dependency providers, Alembic migrations, pytest fixtures, background jobs, and CLI entrypoints.

### TypeScript / JavaScript

Search exports, route handlers, React component usages, type declarations, generated clients, package scripts, test files, and bundler config.

### SQL and data pipelines

Search migrations, model definitions, materialized views, scheduled jobs, downstream dashboards, consumers, and backfill scripts. Identify rollback and compatibility constraints.

## Evidence notation

When reporting evidence, prefer:

- `path:line` when line numbers are available.
- `command -> result summary` when using shell commands.
- `search term -> relevant paths` when line numbers are unavailable.
