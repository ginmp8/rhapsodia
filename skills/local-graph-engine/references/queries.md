# Query semantics

## At a Glance
- **Purpose:** Define deterministic CLI query meanings and bounds.
- **Load when:** Answering questions from `graph.db`, choosing traversal direction, or exporting a focused subgraph.
- **Decision impact:** Prevents semantic reversal of dependencies/dependents and unbounded hairball exports.

## Commands
`find <text>` resolves labels/aliases. `node <id-or-exact-label>` returns properties, aliases, degree, and evidence summary. `neighbors` exposes incident active relations with direction.

`path A B` follows directed edges from A to B by default and returns the shortest BFS path with stable lexicographic tie ordering. Use `--undirected` only when direction is not semantically meaningful.

`impact X --direction dependents` walks **incoming** edges: things that depend on X. `--direction dependencies` walks **outgoing** edges: things X depends on. Default depth is 2; `beyond` counts distinct reachable nodes not shown because they are further away.

`export-view` with no seed exports the full active graph only when it fits `--max-nodes`. For a large graph, choose a seed/depth/filter rather than silently truncating arbitrary nodes.

## SQL
Read-only SQL can be useful for advanced inspection, but normal agent workflows should prefer the stable CLI contract. Do not generate or execute arbitrary write SQL in place of GraphPatch validation/transactions.
