# Layout policy

## At a Glance
- **Purpose:** Route graph shape to a legible, reproducible layout.
- **Load when:** Changing auto-layout behavior or handling a new graph topology.
- **Decision impact:** Prevents "force everywhere", reduces edge hairballs, and preserves deterministic defaults.

## Router
1. Explicit user layout.
2. Valid producer `metadata.layout_hint`.
3. `query.seed` present -> radial focus.
4. All edges directed and the projection is acyclic -> DAG layout (`dagre`).
5. Otherwise -> circular.

Grid is available as an explicit compact alternative. Force maps to G6 `d3-force` and is opt-in only. The builtin fallback intentionally substitutes deterministic circular placement when force is requested and G6 is unavailable.

## Scale
A renderer limit is not a usability target. When a projection becomes a hairball, request a bounded subgraph from the producer by seed/depth/relation/community rather than sampling arbitrary nodes in the browser.
