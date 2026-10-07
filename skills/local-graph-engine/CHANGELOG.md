# Changelog

## 2.0.0
Expanded from graph storage primitives to a domain-neutral local data workbench. Added profiling/mapping, structured/document/code adapters, atomic multi-source ingestion, source claims/revisions, typed queries and aggregates, FTS search, stdlib/optional analytics, snapshots/federation/history, portable exports, local read-only HTTP/MCP, saved queries and explicit outcome memory.
Preserved v1 payloads and original regression fixtures. Added finite/alias/SQL/HTML bounds and tests. New typed queries default to accepted evidence; legacy query scope remains explicit. Default new SQLite journal is DELETE; WAL is opt-in with an upstream patched-version guard. Optional capabilities and their unexecuted runtime checks are documented rather than hidden.
