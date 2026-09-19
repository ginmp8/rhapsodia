# Dependency Tracing Guide

Use this file to build or verify a context map. Search in a stable order so repeated runs do not jump directly to whichever file appears first.

## Canonical search sequence

1. Exact task anchors: supplied path, symbol, endpoint, command, config key, error text, schema/table/topic name.
2. Owning definition: type/function/module, contract, schema, migration, generator source, configuration owner.
3. Direct consumers: calls, imports/exports, implementations, subclasses, handlers, serializers, query projections.
4. Runtime wiring: dependency injection, routers, schedulers, workers, event subscriptions, feature flags, package/build registration.
5. Tests and fixtures: unit, integration, contract, migration, snapshot/golden, smoke, e2e.
6. Boundary consumers: public APIs, generated clients, database views, queues/topics, cross-service contracts, CLI/UI surfaces.
7. Analogous patterns: nearest implementation with the same responsibility.
8. Operational/deployment evidence: CI, containers, infra, docs, rollback/backfill, metrics/alerts when risk requires it.

Use exact-symbol matches before broad domain terms. When equally relevant results remain, prefer the current module/bounded context, then normalized path order.

## Useful local commands

Prefer repository-native indexes/tools when available. Shell examples:

```bash
rg "SymbolName|config_key|endpoint|error message" .
rg "class SymbolName|interface SymbolName|def symbol_name|function symbolName" .
rg "SymbolName" --glob '*test*' --glob '*spec*'
git grep "SymbolName"
git ls-files | rg "name|domain|feature"
```

Do not treat an empty static search as proof that no consumer exists.

## Trace dimensions

- **Definitions/ownership**: source declaration, package/module, build target, CODEOWNERS when present, schema/generator owner.
- **Imports/exports**: modules that import the changed file, barrel exports, public surfaces.
- **Type/contract references**: interfaces, base classes, generics, DTOs, schemas, validators, serialization contracts.
- **Runtime wiring**: DI, routers, handlers, consumers, background jobs, schedulers, feature flags, reflection/convention registration.
- **Data boundaries**: migrations, ORM mappings, queries, projections, indexes, seed data, views, backfills, generated clients.
- **Operational hooks**: metrics, logs, traces, alerts, dashboards, retries, idempotency, locks, ordering, rate limits.
- **Tests**: unit, integration, contract, snapshot/golden, fixture, migration, smoke, e2e.
- **Dynamic/external references**: config strings, route names, topic names, SQL object names, plugin discovery, external clients/repositories.

## Ecosystem hints

### .NET / C#

Search interfaces, handlers, DI registrations, extension methods, options classes, hosted services, EF mappings/migrations, MediatR handlers, validators, serializers, source generators, solution/project references, and test fixtures.

### Python

Search imports, FastAPI/Django/Flask routing, Pydantic models, dependency providers, Alembic migrations, pytest fixtures, entry points/plugins, background jobs, and CLI entrypoints.

### TypeScript / JavaScript

Search exports, route handlers, React/component usages, type declarations, generated clients, package scripts, build aliases, test files, bundler/server config, and convention-based routing.

### SQL and data pipelines

Search migrations, model definitions, views/materialized views, scheduled jobs, downstream transformations/dashboards, consumers, and backfill scripts. Identify rollback and compatibility constraints.

## Evidence notation

Prefer:

- `path:line` for directly inspected evidence;
- `command -> result summary` for measured tool output;
- `search term -> relevant paths` when exact lines are unavailable;
- `inferred: ...` when a dependency relation is reasoned rather than directly observed.
