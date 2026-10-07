# Local graph storage model

## Ownership
Original sources are evidence. The selected `graph.db` is the canonical local working graph; HTML, GraphView, analytics and summaries are derived. Do not rewrite source files to make the graph look consistent.

## Tables
| Tables | Responsibility |
|---|---|
| graph_meta, sources | Contract, extension version, namespace/source hashes and metadata. |
| nodes, edges, node_aliases | Canonical identity, direction, properties and resolution. |
| node_evidence, edge_evidence | v1 indexed evidence for active-structure queries. |
| node_claims, edge_claims | Source-specific full assertions; retain conflicting values and repeated observations. |
| source_revisions, current_revisions, graph_changes | Immutable normalized source revisions, current pointers, ordered mutation log. |
| analysis_runs, node_metrics, communities, community_members | Versioned derived analytics bound to a logical input hash. |
| graph_memory | User/agent query outcomes; never canonical truth or automatic confidence. |
| saved_queries | Validated typed query requests, not stored executable SQL. |
| node_search (optional FTS5) | Search index rebuilt from active entities and aliases. |

## Evidence and conflicts
Provenance: EXTRACTED, DERIVED, INFERRED, MANUAL. Status: accepted, ambiguous, stale, rejected. Confidence measures declared evidence strength, not calibrated truth probability.
When source assertions conflict, retain every claim. For deterministic canonical display, rank status accepted before ambiguous before stale before rejected, then confidence descending, then source URI lexically. Merge compatible attributes only at the best status tier; keep weaker/conflicting values in claims. This rule is a reproducible display policy, not an adjudication of truth.
Rich query output includes full source evidence/claims; v1 evidence tables are indexes and can combine repeated entries with the same legacy locator key. The immutable revision and claim records preserve their separate content.

## Active structure
Legacy v1 views include accepted, ambiguous and stale evidence; rejected evidence does not activate structure. New typed queries default to accepted evidence and can explicitly include ambiguous/stale. Endpoints of selected edges remain available even if their own independent evidence differs; inspect their provenance before conclusions.

## Transaction and refresh
Normalize and validate all source patches before mutation. A batch sees both existing endpoints and endpoints in the same batch. In one transaction, replace only those sources, record revisions, rebuild canonical projections/aliases/search, prune unsupported orphan structure and invalidate stale analytics. Reapplying identical normalized input is a no-op. Failure rolls back the batch.
Source identity must cover all material inputs: source content, mapping/extractor version and declared options. Do not skip a changed mapping just because the source file hash stayed equal.

## SQLite operations
Default new DB journal is DELETE; WAL is explicit and version-guarded. Foreign keys and a five-second busy timeout apply. Never weaken synchronous/durability settings as a generic optimization. One writer at a time, bounded transactions and local disk are the intended operating conditions.
Use the SQLite backup API through `backup` for a consistent portable snapshot, especially when WAL is enabled; never copy only the live DB and discard journal files. Logical graph hash, not physical SQLite bytes, identifies equivalent data.

## Mechanics map
- `scripts/graph.py`: CLI routing; `scripts/graph_engine.py`: v1 contract and compatibility commands.
- `scripts/graph_store.py`: source claims/revisions/transactions; `scripts/graph_journal.py`: journal version policy.
- `scripts/graph_data.py`: record profiling/mapping; `scripts/graph_adapters.py`: bounded source adapters.
- `scripts/graph_query.py`: typed query semantics; `scripts/graph_analysis.py`: derived algorithms.
- `scripts/graph_interop.py`: bundles/history/exports; `scripts/graph_access.py`: bounded read-only SQL/HTTP/MCP.
- `scripts/graph_common.py`: finite JSON, canonical hashing and atomic output guards.
