# Changelog

## 2.2.0
Added finite reader-controlled directed walkthroughs: previous/next/seek/play/pause/replay/speed, upstream/downstream/path modes, SCC cycle groups, parallel structural layers and projected entry/end markers. Added exact relationship readouts, optional follow camera and minimap while retaining manual node movement. Added motion/page-visibility/stale-state guards, canonical export isolation, narrow-screen containment and algorithm/browser regressions. Walkthrough switches an optional G6 view to bundled SVG explicitly. No external runtime asset or new required dependency.

## 2.1.0
Added direct node dragging to the offline SVG viewer, with in-place incident edge updates, zoom/pan-aware coordinates, pointer capture/cancellation and keyboard nudging. Manual positions now survive normal refresh/filter/view operations, and travel in an optional, validated view-state field. Existing v1 states still load; Reset/explicit layout selection removes manual overrides. GraphView/SQLite facts remain unchanged. Added drag configuration and position synchronization for the optional local G6 adapter, plus browser regression tests. No new runtime dependency or remote asset is required.

## 2.0.0
Expanded the standalone viewer into coordinated graph, table, timeline, matrix and numeric-summary views. Added evidence/status/source/property filters, rich claim inspection, focused traversal, safe state/import/export, browser regressions, keyboard alternatives and responsive layout.
Preserved GraphView v1 and original tests. Removed the default remote G6/CDN load; original bundled SVG is fully offline and reviewed local G6 remains optional. Identical material input/assets/config yields byte-identical HTML. Browser tests are actual runtime evidence only for the exercised method/platform.
