# Stable layout policy

## Routing
Explicit layout wins; then a valid producer layout_hint; then a focused query seed -> radial; then a directed acyclic graph -> dagre; otherwise circular. Explicit options also include grid, community and force. The bundled renderer's dagre option is a deterministic layered layout, not a bundled Dagre dependency.
Layered/circular/radial positions are derived from stable node ordering. Community arrangement uses supplied memberships; it does not infer or aggregate canonical entities. Force runs a bounded deterministic local solver (small graphs only), stops and is never a required dependency or ambient animation.

## Readability
Start with an overview appropriate to structure, then filter/focus. Keep direction and relationship labels visible. Large projections are not automatically useful diagrams; select a smaller subgraph when density hides evidence. Graph rendering currently caps 500 nodes/4,000 edges and reports the cap; tables still offer the loaded entity projection. No silent full-database claim.
Parent/child layout is not proof of an organizational hierarchy; repeated IDs or cycles cannot be rewritten merely to fit a tree. Temporal views require actual dated properties, not topological ordering disguised as time.

## Layout state
Pan, zoom, selection and layout choice are user presentation state. Export/restore it against the loaded data identity. Do not save mutable positions as database facts. Respect reduced motion and keyboard alternatives; default transitions do not continuously move the information being read.
