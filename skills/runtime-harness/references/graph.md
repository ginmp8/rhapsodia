# Optional graph projection

`export-graph` returns a `graph-patch-v1` document compatible with a graph consumer such
as Local Graph Engine. The runtime never imports a peer skill or database.

Nodes: Environment, Tool, Skill, Agent and Resource. Edges: observed `records` membership
only. Source URI is stable for the runtime scope while `content_hash` changes with each
immutable snapshot, including incremental observations.

No dependency, permission, ownership, compatibility or workflow edges are inferred.
Absolute paths and environment values are not exported. The graph is for relational
inspection; exact runtime lookup remains the faster JSON registry path.
