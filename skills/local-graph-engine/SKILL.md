---
name: local-graph-engine
description: Build, maintain, validate, query, and export a provenance-first local knowledge graph persisted in a single SQLite file. Use for local graph databases, repository/project knowledge graphs, deterministic node-edge ingestion, source-scoped incremental updates, path/impact/neighborhood queries, GraphPatch ingestion, GraphView export, or optional NetworkX analytics. Do not use primarily for visual graph rendering or UI design; use a graph-explorer/visualization skill for that layer.
---

# Local Graph Engine

## Mission
Own the local graph data plane: versioned ingestion -> SQLite persistence -> deterministic queries -> `graph-view-v1` projection. Keep SQLite as source of truth. Never invent an edge merely to make the graph more complete or attractive.

## Boundary
- **Own:** schema initialization, `graph-patch-v1`, provenance/evidence, idempotent source replacement, validation, search, neighbors, shortest path, impact/reach, bounded subgraphs, `graph-view-v1`, optional analytics.
- **Do not own:** graph UI/layout/rendering, generic code review, semantic claims unsupported by evidence, or host-specific installation behavior.
- Prefer deterministic parsers/adapters for structural edges. If model judgment creates a relation, mark it `INFERRED`; never relabel inference as extraction.

## Quick workflow
1. Resolve a Python 3.10+ launcher and the target database path (default `.local-graph/graph.db`).
2. Run `scripts/graph_engine.py --db <db> init` once.
3. Produce a valid `graph-patch-v1` from a parser, import adapter, or bounded agent extraction. Read [references/graphpatch.md](references/graphpatch.md).
4. Validate before mutation: `... validate-patch <patch.json>`.
5. Apply transactionally: `... apply-patch <patch.json>`. Reapplying the same source replaces only that source's evidence.
6. Query with `find`, `node`, `neighbors`, `path`, `impact`, or `stats`; do not generate arbitrary write SQL.
7. Before visualization, export a bounded `graph-view-v1`: `... export-view <view.json> [--seed <node>]`. Read [references/graphview.md](references/graphview.md).
8. Run `validate-db` after ingestion/repair and before claiming the database is healthy.

## Non-negotiable invariants
- `graph.db` is canonical; HTML/JSON views are projections.
- Every ingested node and edge carries evidence from one declared source.
- Separate canonical entities/relations from evidence so multiple sources can support the same fact without duplicating it.
- Source refresh is **source-scoped replacement**, not whole-database rebuild.
- Active queries use evidence status `accepted|ambiguous|stale`; rejected evidence is retained but does not activate structure.
- Edge endpoints must exist before mutation; invalid patches fail without partial writes.
- Traversal order is stable and bounded; `impact` defaults to depth 2 and reports additional reachable nodes as `beyond`.
- Full exports above the node ceiling must fail with an explicit instruction to focus or raise the ceiling; never silently drop arbitrary nodes.
- Do not apply aggressive cache/mmap/temp-store PRAGMAs by default. Baseline uses foreign keys, busy timeout, and WAL at initialization.
- NetworkX is optional. The standard-library path remains fully functional without it.
- Do not place secrets, credentials, private source contents, or unredacted sensitive values in node properties/evidence unless the user explicitly requires and authorizes that storage.

## Contract and query references
- [references/model.md](references/model.md) — SQLite ownership, tables, active-structure semantics, evidence lifecycle.
- [references/graphpatch.md](references/graphpatch.md) — exact ingestion contract and provenance rules.
- [references/graphview.md](references/graphview.md) — consumer contract shared with visualization tools.
- [references/queries.md](references/queries.md) — CLI semantics, path/impact direction, size bounds, read-only SQL guidance.
- [references/adapters.md](references/adapters.md) — deterministic parser/adaptor policy and safe model-assisted extraction.
- [references/reproducibility.md](references/reproducibility.md) — stable ordering, IDs, timestamps, capability degradation, optional NetworkX.

## Bundled helpers
- `scripts/graph_engine.py` — required, Python stdlib only.
- `scripts/networkx_adapter.py` — optional analytics; requires an installed NetworkX and records its version in each run.
- `examples/basic-patch.json` — minimal valid ingestion example.
- `tests/test_graph_engine.py` — deterministic regression suite.

## Output contract
Return machine-readable JSON from deterministic helpers where supported. Treat `graph.db` as the canonical artifact and `graph-view-v1` as a bounded projection. Report mutation/query/export status, relevant counts, and validation evidence separately from host-runtime claims.

## Stop conditions
Stop before mutation when a patch is invalid, an endpoint is missing, schema/version is unsupported, target identity is ambiguous, or safe transactional execution is unavailable. Never weaken validation or fabricate graph facts to obtain a pass.

## Finalization gate
Before reporting completion after a mutation, run the focused operation, `validate-db`, and the relevant query/export regression. Distinguish structural/package compatibility from actual runtime evidence on a given host. If Python/process execution is unavailable, provide exact commands and mark runtime validation `not-run`; do not claim success.
