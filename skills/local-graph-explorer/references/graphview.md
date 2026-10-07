# GraphView v1 consumer contract

## At a Glance
- **Purpose:** Define what the explorer may trust and render from a `graph-view-v1` producer.
- **Load when:** Integrating a producer, debugging validation, or adding a visual feature that consumes graph fields.
- **Decision impact:** Keeps the explorer read-only with respect to canonical graph facts and prevents UI state from leaking back into the data model.

## Required semantics
`schema_version` must be `graph-view-v1`. `nodes[]` require unique `id`, `label`, and `kind`. `edges[]` require unique `id`, `source`, `target`, `relation`; every endpoint must resolve inside the same view.

`query` explains the projection boundary. `metadata.truncated=true` means the current view is intentionally incomplete. `metadata.layout_hint` is advisory presentation metadata, never graph truth.

Evidence summaries are display/context aids; the explorer does not recalculate their provenance or confidence. Communities may be shown/grouped but do not change canonical nodes or edges.

Layout coordinates, zoom, filters, selection, and path highlight are presentation state and are intentionally not written back to GraphView.
