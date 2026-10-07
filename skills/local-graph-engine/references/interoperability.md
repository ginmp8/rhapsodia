# Snapshots, history and portable exports

## Snapshots and federation
`bundle snapshot.json` exports `graph-bundle-v1`: current complete source patches and logical hash, not all revision history or query memory. `merge other.db --namespace partner` or `merge snapshot.json --namespace partner` imports with namespaced source/entity identities. Identical input is idempotent; similar labels are not merged automatically. Federation changes the destination graph only.
Use the native `backup snapshot.db` command for a full consistent DB copy including history/configuration. It refuses an existing destination and input aliases. A plain copy of a live WAL DB is not a safe substitute.

## Revision operations
`history [--source-uri URI]` reports recorded transitions. `drop-source URI --confirm` writes a tombstone, leaving immutable history. `restore-source URI REVISION --confirm` reapplies the identified revision as a new current transition. These are explicit mutations; back up first for significant datasets.
Version 1 data can be upgraded additively, but lost source-specific values from the older canonical projection cannot be reconstructed. The history starts from recoverable state, never invented earlier facts.
`diff before-view.json after-view.json` compares two GraphView projections. It is a scoped data difference, not proof of a complete source or runtime behavior change.

## Export formats
`export json|graphml|dot|mermaid|csv|wiki OUTPUT [--request request.json]` exports a bounded projection. JSON is GraphView; GraphML carries nodes/edges/properties; DOT/Mermaid describe structure; CSV contains rows with spreadsheet formula defenses; wiki is local linked Markdown suitable for ordinary editors and tools such as Obsidian without requiring them. Wiki refuses an existing output directory.
These are projections. GraphML round trips retain supported structure/properties, not every evidence/history feature. Full-fidelity source exchange uses GraphBundle; full database state uses backup.
Exported portable artifacts may contain source labels, paths, relationships and properties. Review sensitivity before sharing. Do not embed raw credentials, private media or full source bodies by default.

## Usage memory
`remember "question" --nodes ID ... --outcome useful|dead_end|corrected [--note TEXT]` records an explicit outcome. `reflect` reports counts and graph-hash staleness; it does not train a model or generate unquestioned lessons. Do not store sensitive questions/notes without a justified purpose.
Memory entries do not change the logical source graph hash, evidence status or canonical knowledge. A previously useful path still needs revalidation when the data changes.
