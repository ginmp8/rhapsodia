# Query and CLI contract

## Entry point
Resolve `<PYTHON>` and `<ENGINE>` locally. Place `--db` before the subcommand:
`<PYTHON> <ENGINE>/scripts/graph.py --db graph.db query request.json`.
Use JSON files for cross-shell portability; inline JSON is convenient but quoting differs by shell. `--help` is authoritative for implemented arguments.

## Typed requests
| operation | Key arguments |
|---|---|
| find | query; literal text match |
| search | query; FTS5 MATCH syntax when available, explicit substring fallback otherwise |
| node | node (ID or unambiguous exact label/alias) |
| neighbors | node, direction |
| path | node or seed, target, direction, depth, optional nonnegative numeric edge-property weight |
| impact | node or seed, direction=dependents/dependencies, depth |
| subgraph | optional seed, depth, direction, max_nodes |
| stats / quality | evidence/kind/relation filters |
| aggregate | property, metric, optional group_by |
| timeline | time_property, optional from/to ISO time-zone bounds |

Common fields: `kinds`, `relations`, `statuses`, `provenance`, `min_confidence`, `limit`, `offset`, `max_nodes`, `depth`. Unknown fields fail. `graph-query-v1.schema.json` describes a request contract; the request object itself has no schema_version key.
Typed queries default to accepted evidence, depth 2, maximum 500 selected nodes, limit 100. Depth may be 0..100, projection maximum 10,000. Internal graph read budget is 100,000 nodes/200,000 edges. Requests exceeding budgets fail explicitly; do not assume the whole database was searched. The time budget is checked during SQL operations, not a universal CPU deadline.
Direction is structural, not guessed business semantics. Path search uses hop bounds; weighted paths require finite nonnegative values. A missing result may mean no path within the selected projection, evidence filters or depth. Read `search_complete` and bound metadata.
Aggregate numeric values must be explicit numbers, not booleans or silently coerced strings. Define units in the mapping before using sums. Timeline accepts time-zone-qualified ISO timestamps; ambiguous/missing values are reported/excluded rather than guessed.

## Examples
```json
{"operation":"subgraph","seed":"person:42","direction":"both","depth":2,"max_nodes":300}
```
```json
{"operation":"aggregate","property":"budget","metric":"sum","group_by":"kind"}
```
```json
{"operation":"quality"}
```

## Advanced read-only SQL
`... sql "SELECT kind, count(*) AS total FROM nodes GROUP BY kind" --limit 100`.
Only a bounded SELECT query with a restrictive authorizer and function allowlist is supported. No ATTACH, schema writes, extensions, file functions or arbitrary scripts. This is an advanced local inspection surface, not a server-side arbitrary SQL endpoint.

## Saved and legacy queries
`save-query name request.json` stores validated typed requests; `saved-query` lists and `saved-query name` runs them. This changes configuration, not source facts.
Original `find/node/neighbors/path/impact/stats/export-view` commands are retained through `graph_engine.py` with original v1 semantics. They include accepted/ambiguous/stale evidence. Prefer typed `query`/new `export` for evidence filtering and richer claims; disclose the difference rather than silently mixing results.
