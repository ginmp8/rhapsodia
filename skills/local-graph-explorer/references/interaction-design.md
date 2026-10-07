# Coordinated data workspace

## Structure
Compact command bar, scoped filters, dominant data canvas/table and synchronized evidence inspector. The UI is domain-neutral, uses local system fonts, has light/dark/system themes, and does not generate a new design per dataset. No decorative hero, card dashboard or ambient motion.

## Graph and inspection
Search labels, aliases and loaded properties. Filter kind/relation/evidence status/minimum confidence/source/property. Select a node to inspect source claims, evidence and incoming/outgoing relations. Focus by direction/depth and highlight a shortest path over loaded filtered edges. Unsupported or ambiguous source interpretation stays visible, not repaired by the UI.
Pan/zoom graph; keyboard controls and table selection provide alternatives. Source links are displayed as evidence, not fetched or executed. Source payloads use textContent. A richer inspector is available when the producer supplies rich claims; a legacy summary is not expanded into invented evidence.

## Manual node positioning
Primary mouse/touch/pen Pointer Events drag one node, while empty-canvas dragging pans. Pointer capture keeps a gesture active outside the node/canvas; pointer cancellation, capture loss or Escape restores the start position. A 4 CSS-pixel activation threshold separates clicks from movement. Ignore secondary buttons/pointers. Incident paths and hit areas update in place, including parallel edges/self-loops, without restarting layout or fitting the camera during a drag.

Keyboard-focused nodes move by 10 world units with arrow keys, or 50 with Shift+arrows. Enter/Space keeps its selection meaning. A visible help line and grab/grabbing cursors explain the interaction; a screen-reader status announces completed moves. Real touch hardware and comprehensive assistive-technology behavior need separate tests.

Manual positions are presentation overrides. Selection, theme changes, filters/focus and switching coordinated views retain them; Reset, opening another data snapshot or explicitly selecting a layout clears them. View-state v1 adds optional `node_positions`, a mapping from known node IDs to finite numeric `x`/`y` world coordinates bounded to +/-1,000,000. Legacy states without this field remain valid. Reject malformed, excessive or unknown-node coordinates before changing any state. Keep positions only in memory unless the user saves view state; never copy them into GraphView nodes/properties or database records.

## Other views
Table: paginated by 100 entities with properties and synchronized selection. Timeline: explicit ISO timestamps with time zones, up to 400 visible items; missing/invalid values and scope are indicated. Matrix: up to 60 loaded nodes, relationship adjacency, with a visible bound. Summary: counts and explicit numeric values; no unit/currency or business metric inference. Negative numbers keep their sign.
Graph cap is 500 nodes/4,000 edges. Overall import cap is 10,000 nodes/50,000 edges and 32 MiB; choose a producer subgraph above these budgets. All view caps are presentation bounds, not ingestion claims or universal performance guarantees.

## File operations
Open a local GraphView through the browser file chooser; nothing uploads. Save the selected projection as JSON, table rows as protected CSV, graph as SVG/PNG, or portable view-state JSON. State includes validated selection/filter/layout/viewport fields plus optional manual node positions and binds to the loaded projection. The state fingerprint is for compatibility, not authentication.
The live query panel is available only in explicitly started local-server mode. Its requests go to the same 127.0.0.1 origin with a process token. Static files never query a local database by themselves.

## Accessibility and responsive behavior
Visible focus, keyboard node selection, table alternative, labeled controls, no hover-only operation, reduced-motion support, responsive stacked panels and no forced horizontal page overflow. These are implemented controls; comprehensive assistive-technology certification remains a separate validation activity.
