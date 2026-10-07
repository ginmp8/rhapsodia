# GraphPatch v1

## Shape and authority
`graph-patch-v1` is the validated write contract. It is not executable code. Schema: `contracts/graph-patch-v1.schema.json`; semantic endpoint/identity checks also run in the Python validator.

```json
{"schema_version":"graph-patch-v1","source":{"uri":"dataset://study/people","kind":"csv","metadata":{}},"nodes":[{"id":"person:42","kind":"person","label":"Person 42","properties":{},"evidence":[{"provenance":"EXTRACTED","confidence":1,"status":"accepted","locator":"row:2","details":{}}]}],"edges":[]}
```

## Rules
Every node requires nonempty id/kind/label and at least one evidence observation. Every edge requires source/target/relation and evidence. Direction defaults to true; edge IDs are deterministically derived when omitted. Undirected endpoint ordering is canonical. Duplicate entity IDs or canonical edge tuples within one patch fail.
Every endpoint must exist already or in the same atomic batch. Source URI and kind are mandatory. Source hash is optional evidence identity, never proof of source truth. Properties and metadata are finite JSON objects; legacy null optional objects normalize to empty objects. Arbitrary executable payloads are never interpreted.
Use one source URI for an independently refreshable unit. The same source replaces its previous current assertions, not other sources. Separate files normally use separate source URIs. Avoid split batches that could leave cross-source endpoints temporarily unsupported.
Evidence provenance is EXTRACTED/DERIVED/INFERRED/MANUAL; status is accepted/ambiguous/stale/rejected; confidence is numeric 0..1; locator is optional text; details is an object. Preserve observed properties and paths/row/page/line locators where available.
Do not mistake a parser's literal extraction for verification of real-world truth. Model interpretations should normally start ambiguous. Do not combine raw secret values, tokens or private source bodies into a portable artifact without explicit authorized purpose.

## Batch and producer interface
`apply-batch file.json` accepts a JSON array of patches or an object containing `patches`. At most 10,000 patches in one batch. `graph_store.apply_patches` additionally supports an expected-revision map for optimistic concurrency; callers using this Python API must inspect its signature and pass the accepted current revision.
Parsers, another agent, a chat attachment, an export or a standalone tool can produce the same contract. No dependency or host-specific protocol is required. Source content must be present and actually inspected before claiming extraction.
