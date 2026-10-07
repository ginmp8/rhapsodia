---
name: local-graph-explorer
description: Validate and explore evidence-backed GraphView data from any domain as a standalone offline HTML workspace. Use for interactive graph navigation, tables, timelines, relationship matrices, numeric summaries, filters, paths, source inspection or portable visualization. Do not infer canonical facts, mutate a database, or pretend an incomplete projection represents an entire dataset.
---
# Local Graph Explorer

## Mission and boundary
Turn supplied `graph-view-v1` data into useful views without inventing entities, edges, units, dates or evidence. Own presentation, interaction and export of the loaded projection, not database ingestion or canonical graph mutation. Do not assume the data describes software.

## Modes
| Mode | Use |
|---|---|
| Validate | Reject invalid versions, duplicate IDs, missing endpoints, unsafe or oversized payloads. |
| Inspect/layout | Match a stable layout and useful view to the supplied structure and questions. |
| Render | Create a self-contained offline HTML workspace from fixed template, CSS and JavaScript. |
| Explore/export | Filter/focus/search, inspect evidence, trace paths, save projection/view state, export CSV/SVG/PNG. |

## Workflow
1. Obtain a bounded GraphView from any producer. Read [GraphView](references/graphview.md). For raw data, route modeling/ingestion to a data producer first; no specific other skill is required.
2. Resolve Python 3.10+ and package path. Run `<PYTHON> scripts/graph_explorer.py validate view.json`.
3. Run `... layout view.json --layout auto` when structural layout matters. Review [layout policy](references/layout-policy.md); do not use force layout for every graph.
4. Render `... render view.json --output graph.html`. Default output is entirely offline with the bundled SVG renderer. No CDN, external font, account, service, bundler or Node runtime is required.
5. Open in an available browser; verify all relevant interactions, console, network isolation and responsive behavior. When browser execution is unavailable, report that explicitly instead of claiming visual validation.
6. Deliver the HTML, supported view scope, actual render receipt and source/projection bounds. Keep source facts and presentation state separate.

## Five coordinated views
- **Graph:** directed relationships, stable layouts, manual node dragging, focus, search, filters, paths and source inspector.
- **Table:** paginated entity properties and selection; suitable when a graph is not the clearest view.
- **Timeline:** only explicit ISO timestamps with time zones; disclose excluded/ambiguous dates.
- **Matrix:** adjacency from loaded relations; bounded dimensions with clear scope.
- **Summary:** counts and explicit numeric fields; do not infer units, currency, causality or business KPIs.
Read [interaction design](references/interaction-design.md) for display caps and exact behavior.

## Critical invariants
- Root, nodes and edges must validate before output. Render untrusted strings as text, never executable HTML.
- Never turn proximity, color, clustering, visual aggregation or a displayed path into new canonical knowledge.
- Make loaded/filter/display bounds visible. A path not found in this projection is not a global negative claim.
- `auto` routes by explicit hint, seed and graph shape; otherwise use stable circular layout. Force is opt-in, bounded and stops; no decorative continual motion.
- Respect keyboard navigation, focus and reduced motion. Provide a table alternative to canvas interaction.
- Do not fetch source links or send data externally. No telemetry, web storage persistence or remote runtime assets by default.
- Optional G6 requires an explicitly supplied reviewed local bundle; missing bundle in explicit G6 mode is an error. It is not required for the workspace.
- Restore view state only after data-identity and schema validation. Manual node coordinates belong only in view state, never canonical GraphView/SQLite data. Preserve positions through ordinary filtering/redraws; clear them only on data load, Reset or explicit layout selection.
- Identical input, configuration and bundled asset bytes produce identical HTML bytes. Pixel identity across browsers, system fonts and operating systems is not guaranteed.
- In a text-only chat, describe the view or provide a valid projection; do not claim HTML/browser execution. Optional live mode requires a user-started local Engine server.

## Direct references
- [Human quick start](README.md) for installation-independent example commands.
- [GraphView](references/graphview.md), [layout policy](references/layout-policy.md), [interaction design](references/interaction-design.md).
- [G6 local integration](references/g6.md), [portability](references/portability.md), [reproducibility](references/reproducibility.md), [validation](references/validation.md).
- [Research sources](references/sources.md), [third-party notices](THIRD_PARTY_NOTICES.md), [release changes](CHANGELOG.md).
- [GraphView JSON Schema](contracts/graph-view-v1.schema.json) and `examples/fieldwork-view.json` for interoperability.

## Output contract and mechanics
`scripts/graph_explorer.py` validates/routes/exports; `assets/graph-viewer.html`, `assets/viewer.css`, and `assets/viewer.js` are the fixed offline workspace. Keep behavior in these reviewed assets rather than regenerating a new app for each dataset.
Report valid input identity, selected layout, effective renderer, output hash and actual checks. 

## Stop conditions
Reject invalid data or output/input aliases without changing the last-good output. Preserve tests and rerun affected gates after any edit.
