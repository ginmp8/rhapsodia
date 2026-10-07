# GraphView v1 public projection

## Contract
A `graph-view-v1` object contains `nodes` and `edges`; optional `graph`, `query`, `communities`, and `metadata` describe context. Nodes require unique nonempty `id`, `label`, `kind`. Edges require unique nonempty `id`, `source`, `target`, `relation`; endpoints must be present in the same view. Direction defaults to true. See `contracts/graph-view-v1.schema.json` plus the runtime semantic validator.
Node properties, aliases, metrics, community, evidence_summary, evidence and claims are additive. Edge properties/evidence/claims are additive. Producers may preserve compatible unknown metadata; consumers must not execute it. This contract does not expose SQLite tables.

## Evidence and bounds
`query` identifies seed/depth/filter/pagination scope. `metadata.truncated` discloses a capped projection; `eligible_nodes/eligible_edges`, `complete_database`, `evidence_policy`, `source_graph_sha256` and `producer_version` may add context. A non-truncated subgraph is still not necessarily the full dataset. Missing metadata does not establish completeness.
Evidence contains source URI, locator, provenance, confidence, status and details. Evidence summaries support scanning, not verification. Claims preserve differing assertions from sources. `evidence_truncated` marks a bounded inspector payload where supplied.
Communities and metrics are derived analysis, not facts inherent in the source. Data source identities/locators remain available separately from presentation grouping.

## Presentation separation
`metadata.layout_hint` may suggest dagre/radial/circular/grid/community/force. Coordinates, zoom, themes, filters and selection belong to separate view state. Re-exporting a filtered view must recompute its counts and visibly mark scope; it must not replace the producer's canonical database.
A producer can be any local tool or capable chat, not necessarily Local Graph Engine. A consumer can be the Explorer or any program implementing this contract. Original v1 fixtures and their commands remain regression cases.
