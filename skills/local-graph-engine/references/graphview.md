# GraphView v1

## At a Glance
- **Purpose:** Define the stable read projection consumed by graph explorers and other renderers.
- **Load when:** Exporting a subgraph, integrating another visualization tool, or validating engine/explorer compatibility.
- **Decision impact:** Keeps visualization independent of SQLite tables and prevents UI code from becoming a second source of graph truth.

## Contract
Top level:
- `schema_version`: exactly `graph-view-v1`.
- `graph`: counts and producer contract metadata.
- `query`: seed/direction/depth/relation/max-node projection parameters.
- `nodes[]`: `id`, `label`, `kind`, `properties`, aliases, degree, evidence summary, optional community.
- `edges[]`: `id`, `source`, `target`, `relation`, `directed`, `properties`, evidence summary.
- `communities[]`: optional analytics projection.
- `metadata`: truncation, source DB hash, analysis identity, optional layout hint.

## Consumer invariants
- Node IDs are unique.
- Every edge endpoint resolves to a node in the same view.
- Consumers may hide/filter/aggregate data but must not create canonical nodes or edges and present them as source facts.
- `metadata.truncated=true` means the view is intentionally bounded and must not be described as complete.
- Layout positions are presentation state, not graph truth, and therefore are intentionally absent from this contract.

The engine emits pretty, sorted JSON so unchanged database bytes and export options produce stable output.
