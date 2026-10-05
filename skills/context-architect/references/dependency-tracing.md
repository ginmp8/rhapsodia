# Dependency Tracing Guide

## At a Glance

- **Purpose:** Standardize how Context Architect discovers and records repository relationships across semantic, build, syntax, runtime/data-flow, lexical, fuzzy, and historical evidence.
- **Load when:** Locating owning definitions, consumers, reverse dependents, runtime/build wiring, multi-hop impact, or ecosystem-specific dependency paths.
- **Decision impact:** Determines evidence-source strength, typed relation direction, canonical search order, reverse-impact anchors, hop-expansion limits, command heuristics, and how each dependency claim is notated.

## Contents

- Evidence source classes
- Typed relation vocabulary
- Canonical search sequence
- Change-set reverse impact
- Bounded multi-hop traversal
- Useful local commands
- Trace dimensions
- Ecosystem hints
- Evidence notation

Use this file to build or verify a context map. Search in a stable order so repeated runs do not jump directly to whichever file appears first.

## Evidence source classes

Classify how a relation was discovered before treating it as map evidence. Prefer the strongest available source for the relation being claimed; do not convert a weaker class into stronger evidence by wording.

1. **semantic index** — compiler/LSP/SCIP-like definition, reference, implementation, override, symbol or type information;
2. **build/project graph** — project/package/target/task dependencies and reverse dependents from repository-native build metadata;
3. **syntax/AST index** — parser-backed declarations/imports/calls when semantic tooling is unavailable;
4. **runtime/data-flow evidence** — registrations, traces, runtime routes, source-to-sink/data-flow or executed diagnostics when relevant;
5. **exact lexical search** — exact symbol, route, config key, topic, SQL object, error text, serialized name;
6. **semantic/fuzzy retrieval** — discovery aid for candidate files when exact anchors are insufficient;
7. **historical association** — co-change/history signals; supporting evidence only, never sole proof of a dependency.

A source class describes the mechanism, while `measured|observed|supplied|inferred|planned|blocked` describes evidence provenance. Record both when the distinction affects confidence.

## Typed relation vocabulary

Use a concrete relation type instead of the generic word `dependency` when practical:

- `defines`, `declares`, `exports`;
- `references`, `calls`, `called-by`, `imports`;
- `implements`, `implemented-by`, `inherits`, `overrides`;
- `build-depends-on`, `reverse-build-dependent`;
- `runtime-registers`, `routes-to`, `schedules`, `discovers-by-convention`;
- `reads-config`, `writes-config`, `guards-with-flag`;
- `publishes`, `subscribes`, `serializes-as`, `deserializes-as`;
- `reads-data`, `writes-data`, `migrates`, `backfills`;
- `generated-from`, `generates`;
- `tested-by`, `validated-by`;
- `external-api-of`, `depends-on-package-version`;
- `historically-cochanges-with` for weak historical association.

Direction matters. `A calls B` is not interchangeable with `B called-by A`. If a tool reports an undirected relation, preserve that limitation.

## Canonical search sequence

1. Exact task anchors: supplied path, symbol, endpoint, command, config key, error text, schema/table/topic name, or diff/change-set.
2. Owning definition: type/function/module, contract, schema, migration, generator source, configuration owner.
3. Direct consumers: calls, imports/exports, implementations, subclasses, handlers, serializers, query projections.
4. Runtime wiring: dependency injection, routers, schedulers, workers, event subscriptions, feature flags, package/build registration.
5. Tests and fixtures: unit, integration, contract, migration, snapshot/golden, smoke, e2e.
6. Boundary consumers: public APIs, generated clients, database views, queues/topics, cross-service contracts, CLI/UI surfaces.
7. Analogous patterns: nearest implementation with the same responsibility.
8. Operational/deployment evidence: CI, containers, infra, docs, rollback/backfill, metrics/alerts when risk requires it.

Use exact-symbol matches before broad domain terms. Within one relevance class, prefer stronger evidence source classes, then current module/bounded context, then normalized path order.

## Change-set reverse impact

In `review-impact` or when a base/head diff is available:

1. freeze or record the base/head/change-set identity;
2. map changed files to owning symbols/projects/targets;
3. follow direct reverse dependents first (`called-by`, `implemented-by`, `reverse-build-dependent`, public consumers);
4. expand to transitive reverse dependents only while the selected evidence tier requires it;
5. include dependency/lockfile changes when repository-native tooling can map resolved dependency changes to affected projects;
6. stop at explicit external boundaries and record unresolved consumers rather than guessing.

Repository-native affected/project graph commands are preferred when available, but no specific build system is required by the skill.

## Bounded multi-hop traversal

Multi-hop traversal is selective, not exhaustive.

- `hop 0`: task/change-set anchor or owner.
- `hop 1`: direct consumers, implementations, runtime registrations, tests, direct build dependents.
- `hop 2+`: expand only when a relation crosses a relevant boundary, explains runtime behavior, reaches a contract/test/validation surface, or opens a new risk class.
- Record hop/depth for material secondary evidence when it helps explain why the file is in scope.
- Prefer a repository-native depth bound when one exists. Otherwise apply the same bound conceptually.
- Unknown dynamic consumers or write/read overlap keep the branch provisional; they do not justify unbounded traversal.

Stop a traversal branch when it reaches an already-covered node with no new relation class/risk, an explicit out-of-scope boundary, or the selected-tier closure criteria.

## Useful local commands

Prefer repository-native semantic/build indexes when available. Shell examples are fallbacks:

```bash
rg "SymbolName|config_key|endpoint|error message" .
rg "class SymbolName|interface SymbolName|def symbol_name|function symbolName" .
rg "SymbolName" --glob '*test*' --glob '*spec*'
git grep "SymbolName"
git diff --name-only <base>...<head>
git ls-files | rg "name|domain|feature"
```

Do not treat an empty static search as proof that no consumer exists.

## Trace dimensions

- **Definitions/ownership**: source declaration, package/module, build target, CODEOWNERS when present, schema/generator owner.
- **Imports/exports**: modules that import the changed file, barrel exports, public surfaces.
- **Type/contract references**: interfaces, base classes, generics, DTOs, schemas, validators, serialization contracts.
- **Runtime wiring**: DI, routers, handlers, consumers, background jobs, schedulers, feature flags, reflection/convention registration.
- **Data boundaries**: migrations, ORM mappings, queries, projections, indexes, seed data, views, backfills, generated clients.
- **Operational hooks**: metrics, logs, traces, alerts, retries, idempotency, locks, ordering, rate limits.
- **Tests**: unit, integration, contract, snapshot/golden, fixture, migration, smoke, e2e.
- **Dynamic/external references**: config strings, route names, topic names, SQL object names, plugin discovery, external clients/repositories.

## Ecosystem hints

### .NET / C#

Prefer compiler/LSP symbol references when available. Search interfaces, handlers, DI registrations, extension methods, options classes, hosted services, EF mappings/migrations, MediatR handlers, validators, serializers, source generators, solution/project references, central package/lock files, and test fixtures.

### Python

Search imports, FastAPI/Django/Flask routing, Pydantic models, dependency providers, Alembic migrations, pytest fixtures, entry points/plugins, background jobs, and CLI entrypoints.

### TypeScript / JavaScript

Search exports, route handlers, React/component usages, type declarations, generated clients, package scripts, project graphs, lockfiles, build aliases, test files, bundler/server config, and convention-based routing.

### SQL and data pipelines

Search migrations, model definitions, views/materialized views, scheduled jobs, downstream transformations/dashboards, consumers, and backfill scripts. Identify rollback and compatibility constraints.

## Evidence notation

Prefer:

- `path:line` for directly inspected evidence;
- `command -> result summary` for measured tool output;
- `semantic index -> symbol/relation -> paths` for compiler/LSP/SCIP-like evidence;
- `build graph -> target -> reverse dependents` for project/build evidence;
- `search term -> relevant paths` for lexical discovery;
- `inferred: ...` when a dependency relation is reasoned rather than directly observed.
