# Changelog

## 2.1.0
Added read-only `context` queries with exact canonical UTF-8 byte budgets, compact/evidence detail, property allowlists, source dictionaries, explicit scope/uncertainty and snapshot/profile-bound caller-held reuse. Added the context result contract, shared CLI/MCP request schema, same-selection byte measurement helper and focused regression tests. No SQLite migration, new runtime dependency, cloud/model call or change to GraphView/legacy queries. Generated Roslyn obj artifacts are excluded from distribution.

## 2.0.0
Expanded from graph storage primitives to a domain-neutral local data workbench. Added profiling/mapping, structured/document/code adapters, atomic multi-source ingestion, source claims/revisions, typed queries and aggregates, FTS search, stdlib/optional analytics, snapshots/federation/history, portable exports, local read-only HTTP/MCP, saved queries and explicit outcome memory.
Preserved v1 payloads and original regression fixtures. Added finite/alias/SQL/HTML bounds and tests. New typed queries default to accepted evidence; legacy query scope remains explicit. Default new SQLite journal is DELETE; WAL is opt-in with an upstream patched-version guard. Optional capabilities and their unexecuted runtime checks are documented rather than hidden.
