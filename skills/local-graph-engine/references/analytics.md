# Analytics without source mutation

## Built-in algorithms
`analyze components|scc|cycles|degree|pagerank` uses Python stdlib. Components use undirected reachability; SCC preserves direction; cycles reports strongly connected cyclic regions and self-loops, not enumeration of all simple cycles. PageRank has fixed damping, iteration ceiling and convergence tolerance. Nonconvergence is an error, not a partial success.
Analytics selects accepted evidence, maximum 20,000 nodes/100,000 edges. Results contain algorithm, backend/version, parameters, source logical hash and derived run ID. A changed graph during computation prevents commit; old results become stale and are not relabeled current.

## Optional NetworkX
Explicit `--backend networkx` enables `communities` (greedy modularity), `louvain`, `leiden`, `betweenness`, `closeness` when the installed NetworkX exposes that capability. No silent algorithm substitution. Exact centrality is capped at 2,000 nodes. Louvain/Leiden receive an explicit seed; record installed version and projection parameters for replay.
The analytics projection converts parallel relations to edge multiplicity weights; this does not modify stored relationships. Communities are exploratory groupings, not asserted departments or domain facts. Use evidence to name them rather than treating a statistical group as a confirmed classification.
The tested optional environment is documented in validation; availability of an optional module does not prove every algorithm was executed. A fixed seed cannot guarantee bit-identical results across library/BLAS/platform versions.

## Using results
Group membership and metrics can appear in GraphView and the inspector. Use them to prioritize exploration, not to declare business importance without context. Usage outcomes in graph_memory are separate and never silently adjust PageRank, accepted evidence or source confidence.
