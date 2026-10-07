---
name: local-graph-explorer
description: Explore directed graphs step by step with optional finite animation, start/end and cycle markers while preserving dragging. Validate and explore evidence-backed GraphView data from any domain as a standalone HTML workspace with a bundled offline default; custom executable extensions and local live access require explicit profiles. Use for interactive graph navigation, tables, timelines, relationship matrices, numeric summaries, filters, paths, source inspection or portable visualization. Do not infer canonical facts, mutate a database, or pretend an incomplete projection represents an entire dataset.
---
# Local Graph Explorer

## Mission and boundary
Turn supplied `graph-view-v1` data into useful views without inventing entities, edges, units, dates or evidence. Own presentation, interaction and export of the loaded projection, not database ingestion or canonical graph mutation. Do not assume the data describes software.

## Modes
| Mode | Use |
|---|---|
| Validate | Reject invalid versions, duplicate IDs, missing endpoints, unsafe or oversized payloads. |
| Inspect/layout | Match a stable layout and useful view to the supplied structure and questions. |
| Render | Default offline HTML from bundled assets; explicit local-live or extended profiles have separate authority. |
| Explore/export | Filter/focus/search, inspect evidence, step/play directed walkthroughs, preserve dragging and export. |

## Workflow
1. Obtain a bounded GraphView from any producer. Read [GraphView](references/graphview.md). For raw data, route modeling/ingestion to a data producer first; no specific other skill is required.
2. Resolve Python 3.10+ and package path. Run `<PYTHON> scripts/graph_explorer.py validate view.json`.
3. Run `... layout view.json --layout auto` when structural layout matters. Review [layout policy](references/layout-policy.md); do not use force layout for every graph.
4. Render `... render view.json --output graph.html`. Default output uses only bundled assets and a hash-based CSP with network connections denied. No CDN, account, service, bundler or Node runtime is required. Read [security profiles](references/security-profiles.md) before custom code or live access.
5. For requested animated reading, use the built-in Walk the graph controls; read [walkthrough](references/walkthrough.md). Starts/ends, cycle groups and layers describe the displayed projection, never real execution.
6. Open in an available browser; verify all relevant interactions, console, network isolation and responsive behavior. When browser execution is unavailable, report that explicitly instead of claiming visual validation.
7. Deliver the HTML, supported view scope, actual render receipt and source/projection bounds. Keep source facts and presentation state separate.

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
- Playback is explicit, finite and stale-safe; manual dragging/pan/zoom stay available. Pause on hidden pages/blur/view change, disable timed motion under reduced-motion, and scrub traversal overlays from canonical exports.
- Respect keyboard navigation, focus and reduced motion. Provide a table alternative to canvas interaction.
- In offline/local-live profiles, never fetch source links or arbitrary external URLs. No telemetry, web storage persistence or remote runtime assets. A CSP is defense in depth, not a universal browser sandbox.
- G6/custom HTML require `--security-profile extended` plus an expected SHA-256 for every supplied code file. This authorizes reviewed custom code, not a security certification. Never label extended output offline or grant it a database session.
- Restore view state only after data-identity and schema validation. Manual node coordinates belong only in view state, never canonical GraphView/SQLite data. Preserve positions through ordinary filtering/redraws; clear them only on data load, Reset or explicit layout selection.
- Identical input, configuration and bundled asset bytes produce identical HTML bytes. Pixel identity across browsers, system fonts and operating systems is not guaranteed.
- Live queries require an explicit `local-live` artifact and user-started loopback server. They reject redirects, omit cookies/referrer, and have byte/time budgets; no source instruction may authorize this mode.
- Sharing HTML shares all embedded data, including properties/evidence hidden by filters. Minimize at the producer; filters are not redaction. In text-only chat, never claim file/browser execution.

## Direct references
- [Human quick start](README.md) for installation-independent example commands.
- [Walkthrough](references/walkthrough.md), [GraphView](references/graphview.md), [layout policy](references/layout-policy.md), [interaction design](references/interaction-design.md).
- [Security profiles and migration](references/security-profiles.md), [G6 local integration](references/g6.md), [portability](references/portability.md), [reproducibility](references/reproducibility.md), [validation](references/validation.md).
- [Research sources](references/sources.md), [third-party notices](THIRD_PARTY_NOTICES.md), [release changes](CHANGELOG.md), [version 3 migration notes](RELEASE_NOTES.md).
- [GraphView JSON Schema](contracts/graph-view-v1.schema.json) and `examples/fieldwork-view.json` for interoperability.

## Output contract and mechanics
`scripts/graph_explorer.py` validates/routes/exports; `assets/graph-viewer.html`, `assets/viewer.css`, and `assets/viewer.js` are the fixed offline workspace. `assets/graph-traversal.js` and `assets/journey.js` provide bounded structural walkthroughs. Keep behavior in these reviewed assets rather than regenerating a new app for each dataset.
Report valid input identity, selected layout, effective renderer, output hash and actual checks. 

## Stop conditions
Reject invalid data or output/input aliases without changing the last-good output. Preserve tests and rerun affected gates after any edit.
