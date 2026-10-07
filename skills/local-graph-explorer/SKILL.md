---
name: local-graph-explorer
description: Validate and visualize a local graph projection as an interactive deterministic HTML workspace. Use with `graph-view-v1` data to render searchable/filterable node-edge maps, inspect evidence and properties, highlight paths and dependency direction, choose structure-appropriate layouts, or generate a local Graph HTML using AntV G6 with an offline fallback. Do not use to create, infer, persist, or mutate canonical graph facts; a graph engine/data skill owns that layer.
---

# Local Graph Explorer

## Mission
Own the presentation layer for an existing `graph-view-v1`. Render what the producer supplied; never invent nodes, edges, dependencies, or evidence. The graph contract, not the HTML, is source truth.

## Boundary
- **Own:** GraphView validation, deterministic layout routing, filtering/search, selection, path highlighting, inspector UX, theme/accessibility, HTML generation.
- **Do not own:** SQLite schema, ingestion, edge inference, source refresh, parser correctness, or canonical graph mutation.
- AntV G6 5.1.1 is the preferred renderer. The bundled vanilla-SVG backend is a local/offline fallback, not a second semantic model.

## Quick workflow
1. Obtain a bounded `graph-view-v1` from the graph producer. Read [references/graphview.md](references/graphview.md).
2. Resolve Python 3.10+ and run `scripts/graph_explorer.py validate <view.json>`.
3. Inspect the layout decision with `... layout <view.json> --layout auto` when graph shape matters.
4. Render: `... render <view.json> --output graph.html`.
5. For fully offline G6, provide a reviewed local `g6.min.js` via `--g6-js`; otherwise the generated HTML uses the pinned 5.1.1 CDN and falls back to the bundled SVG renderer if G6 is unavailable.
6. Open `graph.html` locally and verify search, filters, selection, path, inspector, theme, and the expected layout.

## Deterministic layout policy
- Explicit `--layout` wins.
- Then honor a valid producer `metadata.layout_hint`.
- Focused view with `query.seed` -> `radial`.
- Directed acyclic graph -> `dagre`.
- Otherwise -> `circular`.
- `force` is opt-in only because physics can introduce avoidable run-to-run placement variance.
Read [references/layout-policy.md](references/layout-policy.md) before changing these rules.

## Non-negotiable invariants
- Reject unsupported schema versions, duplicate node/edge IDs, and edges with missing endpoints before writing HTML.
- The viewer may filter, dim, aggregate visually, or calculate a path over loaded edges; it must not create canonical graph facts.
- Keep graph data escaped inside the HTML; user/source strings must be displayed as text, not interpreted as HTML.
- No ambient animation, pulsing, drifting, or automatic layout churn. Motion follows user action and must respect reduced-motion preferences.
- Incoming and outgoing direction must remain distinguishable when a node is selected.
- A bounded/truncated projection must remain visibly identified as bounded; never present it as the entire graph.
- Do not render a huge full graph merely because the renderer can. Ask the producer for a focused subgraph when legibility degrades.
- Generated HTML must be byte-stable for identical input/config/template bytes.

## UI and renderer references
- [references/graphview.md](references/graphview.md) — exact consumer contract and evidence fields.
- [references/layout-policy.md](references/layout-policy.md) — layout routing, graph-shape rules, force restrictions.
- [references/interaction-design.md](references/interaction-design.md) — dense developer-workspace UX, direction colors, filtering, path and inspector behavior.
- [references/g6.md](references/g6.md) — pinned G6 5.1.1 usage and known version pitfalls.
- [references/reproducibility.md](references/reproducibility.md) — stable bytes, offline behavior, capability/reporting limits.

## Bundled resources
- `scripts/graph_explorer.py` — validator/layout router/renderer; Python stdlib only.
- `assets/graph-viewer.html` — deterministic HTML workspace template with G6 preferred + SVG fallback.
- `examples/basic-view.json` — portable GraphView fixture.
- `tests/test_graph_explorer.py` — deterministic regression suite.

## Output contract
Produce a validated `graph.html` plus a concise render receipt identifying input identity, layout, backend, and output identity when available. The HTML is a projection only; never present visual filtering or aggregation as mutation of canonical graph facts.

## Stop conditions
Stop before render when `graph-view-v1` is invalid, IDs are duplicated, edge endpoints are missing, the schema version is unsupported, or the template cannot be loaded safely. If G6 is unavailable in `auto` mode, degrade to the bundled renderer; do not invent structure to compensate.

## Finalization gate
After generating HTML, run the validation and render regression appropriate to the requested backend. Static/template tests prove package mechanics, not actual G6/browser behavior. If a browser runtime is available, load the result and check console/interactions; otherwise report browser validation `not-run` instead of claiming it.
