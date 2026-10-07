# Graph storage model

## At a Glance
- **Purpose:** Define canonical SQLite ownership and evidence semantics.
- **Load when:** Designing ingestion, migrations, pruning, deduplication, or direct SQL reads.
- **Decision impact:** Prevents duplicated facts, source-wide destructive refreshes, and queries that treat rejected evidence as active structure.

## Canonical model
`graph.db` stores canonical `nodes` and `edges` separately from the assertions that support them.

| Table | Responsibility |
|---|---|
| `sources` | One stable source identity per URI plus optional content hash/metadata |
| `nodes` | Canonical entity identity, kind, label, properties |
| `node_aliases` | Source-scoped alternate labels for resolution/search |
| `edges` | Canonical relation identity and direction |
| `node_evidence` | Source/provenance/confidence/locator/status supporting a node |
| `edge_evidence` | Source/provenance/confidence/locator/status supporting an edge |
| `analysis_runs` | Identity/version/parameters of optional analytics |
| `node_metrics` | Metrics produced by an analysis run |
| `communities` / `community_members` | Optional community projection from one analysis run |

## Active structure
A node is active when it has non-rejected evidence or participates in an active edge. An edge is active when at least one evidence row is `accepted`, `ambiguous`, or `stale`. `rejected` evidence is historical/accounting data and does not activate a relation.

## Source refresh
Applying a patch for an existing source URI must:
1. validate the complete patch before writes;
2. delete only aliases/evidence owned by that source;
3. upsert canonical nodes/edges and insert the new evidence;
4. prune canonical edges with no evidence and nodes with no evidence or incident edges;
5. rebuild optional search state;
6. commit atomically.

Never delete evidence owned by another source during refresh.

## IDs
Prefer caller-supplied, namespaced stable node IDs such as `file:src/auth.cs`, `symbol:Namespace.Type`, or `concept:jwt`. Canonical edge IDs are deterministically derived from `(source,target,relation,directed)` when omitted. Source and evidence IDs are also deterministic hashes of canonical content.

## SQLite posture
Use foreign keys and a busy timeout on every connection. Enable WAL during initialization. Do not hard-code cache size, mmap size, temp-store, or synchronous tuning as universal defaults; benchmark before adding them for a concrete workload.
