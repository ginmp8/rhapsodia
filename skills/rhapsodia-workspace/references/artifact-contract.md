# Source-owned artifact contract v1

The authoritative envelope is `artifact-envelope.schema.json`; the action receipt is `artifact-actions.schema.json`. These schemas are closed and have no remote references. Runtime validation additionally checks real calendar dates, ownership namespaces, path containment, hashes, privacy consistency, and lifecycle/source coherence.

A sidecar is exactly `<source path>.artifact.json`. `artifact_id` begins with `producer:` and is stable when a source is edited. `work_item_id` is a correlation key, not a Board, execution state, or technical planning ID. `workflow_id` is optional transport correlation. An artifact's metadata timestamps describe publication, not the creation time encoded by another domain's semantic ID.

The source hash covers exact bytes. A modification without republication is stale and blocks indexing. Each producer chooses its own root and artifact types. No central writable registry, Workspace process, peer code, or UI is required for publication.

States are pairs: `dimension` and `value`. Keep `governance`, `planning`, `execution`, `validation`, and `release` separate. A state is the producer's attributed statement, not an independent audit. Never infer delivery completion from a file, successful index, planning-ready state, or test result.

Relations use stable artifact IDs, not filesystem lookup expressions. `depends_on` cycles fail; other relation kinds can describe legitimate feedback loops. Missing target IDs generate explicit warnings because a selected source scope may be partial. Removed targets are not counted as live dependencies. A `removed` tombstone preserves its last source hash while the source is absent; deleting the tombstone intentionally also removes discoverable history.

The catalog stores record, sidecar path and sidecar hash. Its fingerprint binds the selected roots, destination, metadata and source hashes. Rebuilding from the same bytes produces identical JSON/HTML. Generated files do not contain absolute host paths or source body copies.

Workspace has no write-back command. Domain edits are new requests for the source owner. Publisher receipts are audit evidence, not credentials; a malicious local filesystem writer remains inside the filesystem trust boundary.
