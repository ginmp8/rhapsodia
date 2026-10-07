# Local Graph Explorer 2.1

An offline, data-led workspace for GraphView: graph, table, timeline, adjacency
matrix and summary. It never requires G6, a CDN, an application account or a
server. Original graph data is not modified by visual interaction.

## Start with a working example

From this skill directory, using an available Python 3.10+ launcher:

```text
python scripts/graph_explorer.py validate examples/fieldwork-view.json
python scripts/graph_explorer.py render examples/fieldwork-view.json --output graph.html
```

Open `graph.html` in a browser. It embeds data, code and styles, so it can work
offline after generation. Python is not needed simply to open the generated HTML.
Use Open data to load another GraphView JSON. User strings are displayed as text.

## Explore

Search; filter entity/relationship/evidence types; select a node for properties
and source evidence; focus a neighborhood; find paths over the loaded graph;
change a stable layout; inspect dates, matrix cells or numeric properties.
Save a filtered projection or view state explicitly. A filtered/bounded view is
not the entire database, and a missing local path is not a global negative claim.

## Move nodes

Drag a node with the primary mouse button or touch; drag empty canvas to pan.
Connections follow the node, including parallel edges and self-loops. A click
still selects; a drag does not become an accidental click or move the camera.
Focus a node with Tab, then use arrow keys (10 world units) or Shift+arrows
(50 units). Escape cancels an active pointer drag and restores its starting point.

Manual coordinates survive selection, filters, theme changes and switching views.
Use **Export > View state > Save**, then **Load state**, to keep them across
sessions. Nothing is stored silently in the browser or written to the source
GraphView/SQLite database. **Reset** or explicitly choosing a layout clears the
manual coordinates and regenerates automatic positions. SVG/PNG exports use the
current visual positions; GraphView JSON remains data-only.

## Optional integration

A reviewed local G6 bundle can be embedded with `--g6-js`; explicit G6 mode
without a bundle fails rather than contacting a CDN. Native SVG remains the
fully functional default. See `references/g6.md` for version/coverage limits.
A separately started Engine local HTTP server enables live read-only queries.
A server is never needed for a snapshot and is never started by rendering HTML.

## Validation and license

Run `python -B -m unittest discover -s tests -v`. Actual browser tests additionally
need installed Playwright and Chromium. Without them, the browser class skips;
static tests alone do not establish browser compatibility.
This package is MIT-licensed. See LICENSE and THIRD_PARTY_NOTICES.md.
Host-neutral instructions require a capable agent runtime; an arbitrary text-only
chat cannot execute Python or preview HTML simply because this skill exists.
