# Evidence intermediate representation, SQLite graph and traceability

**Purpose:** consolidate multi-format static evidence into a reusable, incremental directed graph with stable identities.
**Load when:** many files/formats must be correlated, a decompiler/Roslyn report must join an inventory, or evidence needs queryable local persistence/export.
**Decision impact:** governs graph identity, provenance tiers, partial coverage, deduplication, caching and source-to-claim verification.

## Create / update / export

```sh
<PYTHON> scripts/workbench.py trusted-or-untrusted-input.zip -o static.json --full
<PYTHON> scripts/evidence_ir.py build static.json --sqlite evidence.sqlite -o evidence-ir.json
<PYTHON> scripts/evidence_ir.py build second-static.json --sqlite evidence.sqlite -o second-import.json
<PYTHON> scripts/evidence_ir.py export --sqlite evidence.sqlite -o graphview.json
```

Core supports JSON reports from `workbench.py`, individual supported analyzers, `tool_adapters.py` and imported Roslyn evidence. `normalize` produces `nodes[]` and `edges[]` with `id`, `kind`, `evidence_level`, `anchor`, `artifact` and exact report SHA. Artifact / method / candidate call-target / route / symbol nodes are **not** automatically resolved runtime call graphs. `reported` source ID uses the exact report-byte SHA-256; output identity includes that SHA and content anchors, not mutable filename order.

SQLite stores `sources`, `nodes`, `edges` with foreign keys and indexes. Re-importing exactly identical report bytes returns `unchanged-reused` and does not duplicate nodes or edges. New distinct report hashes remain as separate evidence versions; automatic old-version deletion is deliberately not attempted. Export is bounded and produces JSON for interactive graph-view consumers; it does not bundle a server/UI/database daemon. Outputs can carry filenames/symbol names, so store locally and review before sharing publicly.

## Assurance labels

- `declared`: explicitly decoded metadata, routes, or symbol names.
- `lexical_candidate`: text pattern, not a semantic compiler reference.
- `decoded_call_site`: instruction operand/reference at a particular bytecode offset; may not resolve dynamic dispatch.
- `claimed_semantic_resolution`: imported compiler/exported data with metadata but no independently executed compile on this host.
- `runtime_observed`: authorized execution with actual receipt; never created from static metadata alone.
- `unknown`: unresolved implementation, state or behavior; report as missing instead of fabricating edges.

The corpus and tool versions must remain frozen for reproducible claims. Source, requirement, modification, scenario and evaluation IDs in external research traceability reports must be bidirectionally linked; a graph merely *visualizing* a claim is not validation of that claim.

## Integration gates

Use `python3 -m unittest discover -s tests -q` and inspect exit status. A `workbench.py` code `3` is **partial** analysis, not absence of missing behavior. Verify current source SHA, tool versions, parser limits, graph import identities, testing scope, original-vs-candidate mismatch reports and unresolved unknowns. Preserve research/evaluation snapshots outside the target ZIP and package only exact validated files. No GraphView renderer dependency is required for the skill to generate the portable graph JSON.
