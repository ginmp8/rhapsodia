# Changelog

## 3.2.0 - 2026-10-16

Add backward-compatible `workspace-knowledge-v2` advisory execution lessons and read-only `review-lessons` grouping on distinct source-pinned episodes. Old v1 references/remedies and graph storage remain supported without migration or a new dependency. No automatic instruction/test changes, evaluator rewrites, or agent authorization; only an independent owner-controlled promotion can adopt a suggestion. Add focused negative, stale-source, conflict, revision and legacy-compatibility regressions.

## 3.1.0 - 2026-10-16

Same-release clarification in RhapsodIA 0.11.0: Explain structural versus operational memory, relevance and nonduplicate learning, same-question reuse, explicit no-new-knowledge outcomes and preservation of non-reconstructible experiences. Add a direct learning guide; schemas and CLI behavior are unchanged.

Add bounded per-workspace GraphPatch memory with idempotent start, source pins, graph-first lookup, typed troubleshooting recipes, expected-revision updates, serialized writers and conservative reconciliation. Existing graph/data/view schemas remain unchanged.

## [3.0.0] - 2026-10-07

### Fixed
- Package/runtime metadata now derives `PACKAGE_VERSION` from the canonical `VERSION` file, preventing `doctor`, typed GraphView `producer_version`, and GraphBundle metadata from reporting the stale 2.1.0 value.

### Security
- Hardened optional HTTP access: the chosen artifact must explicitly implement local-live HTML runtime v1. Validate its profile, early CSP, inline script hashes and empty inert session slot before binding or granting a token. The server snapshots validated bytes, preserves hash-authorized scripts, refuses custom/offline pages, rejects duplicate authority headers and unsupported request framing, and exposes optional expected-viewer hash pinning. Added authorization and artifact-boundary regressions.

### Changed
- Breaking migration: regenerate local-live HTML before using serve; old offline/custom viewers are no longer upgraded automatically. Native SQLite, ingestion, read-only queries, context budgeting/reuse, exports and MCP retain their contracts; no database migration or new required dependency. See references/live-viewer-contract.md for operator, trust and rollback guidance.

## 2.1.0
Added read-only `context` queries with exact canonical UTF-8 byte budgets, compact/evidence detail, property allowlists, source dictionaries, explicit scope/uncertainty and snapshot/profile-bound caller-held reuse. Added the context result contract, shared CLI/MCP request schema, same-selection byte measurement helper and focused regression tests. No SQLite migration, new runtime dependency, cloud/model call or change to GraphView/legacy queries. Generated Roslyn obj artifacts are excluded from distribution.

## 2.0.0
Expanded from graph storage primitives to a domain-neutral local data workbench. Added profiling/mapping, structured/document/code adapters, atomic multi-source ingestion, source claims/revisions, typed queries and aggregates, FTS search, stdlib/optional analytics, snapshots/federation/history, portable exports, local read-only HTTP/MCP, saved queries and explicit outcome memory.
Preserved v1 payloads and original regression fixtures. Added finite/alias/SQL/HTML bounds and tests. New typed queries default to accepted evidence; legacy query scope remains explicit. Default new SQLite journal is DELETE; WAL is opt-in with an upstream patched-version guard. Optional capabilities and their unexecuted runtime checks are documented rather than hidden.
