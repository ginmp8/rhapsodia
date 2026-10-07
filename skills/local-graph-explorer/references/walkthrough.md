# Structural walkthrough and motion

## Reading a directed graph
The Walk the graph panel operates only on the currently displayed, filtered projection (at most 500 nodes and 4000 edges). Choose Downstream, Upstream or Directed path. Optionally choose a starting entity; a path requires both endpoints. Press Prepare, then use Previous/Next, the step slider, chapter buttons or Play/Pause. Playback is finite and reader-started; Replay restarts intentionally. Speed is 0.5x, 1x or 2x. Preparing a graph never starts animation automatically.

IN and END are entry/end **members of this projection**, not claims about the original system. An isolated entity has both roles. A strongly connected component receives CYCLE markers and stays one grouped step; no false internal beginning/end is invented. Independent components can appear in the same topological layer, which is not evidence of runtime parallelism. Undirected edges remain visible but are excluded from ordered traversal and counted explicitly. Paths use actual directed edges and deterministic shortest-hop selection; an unreachable endpoint clears the previous walkthrough.

The current layer and arriving relationships are highlighted. The readout names current entities and at most three exact relationship facts in their **original direction**, including when reading upstream. Further relationships remain inspectable. Visited means read, not executed. This viewer is not a process runner, execution log or live telemetry monitor.

## Move without losing the walkthrough
Drag nodes, pan empty canvas, zoom or use keyboard movement as usual while stepping or playing. Positions are presentation state and never overwrite GraphView/SQLite facts. Normal theme/view/filter operations preserve manual positions under the existing position contract. Filters/data changes invalidate the walkthrough; switching away from Graph pauses it. Follow camera is opt-in and yields immediately to a manual pan/drag/zoom or minimap gesture. The minimap reflects real positions; click to recenter, or focus it and press Enter/Space to fit.

Node movement only updates incident geometry and schedules bounded minimap refreshes; it does not recompute the walkthrough or restart a layout. Changing a layout or Reset retains the original explicit position-reset behavior. Save/Load View state continues to save validated coordinates/camera/filter choices; walkthrough timers and progress are intentionally not persisted. Loading state stops playback.

## Motion and accessibility
Reduced-motion preferences disable timed playback and edge animation, but manual steps remain available. Hidden pages, window blur and leaving the graph view pause playback. Epoch checks cancel stale timers after data/filter/direction/reset changes. Speed changes reschedule only the one active timer. There is no perpetual decorative force simulation. Controls are native keyboard-operable elements; node/table access remains available.

On narrow screens the graph panel and filters follow normal page flow without overlap. Desktop graph bounds stay visible; zoom/focus/table remain necessary for dense projections. No pixel identity across browsers or universal physical-input support is claimed.

## Data and exports
Original GraphView topology, evidence and properties are unchanged. SVG/PNG exports retain current manual geometry but remove transient traversal/entry/cycle overlays and motion. GraphView export stays data-only. Table/timeline/matrix/summary behavior remains unchanged. The minimap is a navigation aid, not a second graph database.

Walkthrough uses the bundled SVG renderer. If a reviewed optional G6 view is active, preparing a walkthrough explicitly switches to the local SVG presentation; it does not pretend to animate the third-party renderer. No G6 bundle, CDN, Node runtime, server, account, other skill or reference project is needed for the delivered HTML.

## Mechanics and checks
`assets/graph-traversal.js` owns deterministic reachability, shortest directed paths and iterative SCC condensation. `assets/journey.js` owns finite reader state and camera/DOM interaction. `viewer.js` remains the workspace/geometry owner. The assets are embedded by `scripts/graph_explorer.py`, never generated afresh per dataset.

Run all Python tests with `python -B -m unittest discover -s tests -v`. Browser checks require available Playwright and Chromium; missing tools are explicit skips, not runtime passes. The standalone algorithm can also be checked with `node tests/test_traversal.cjs assets/graph-traversal.js`. Node is only an optional test tool, not a generation or viewing dependency.
