# GraphPatch v1

## At a Glance
- **Purpose:** Define the only supported write contract for normal graph ingestion.
- **Load when:** Creating/importing/updating graph facts from files, parsers, agents, JSON, or other systems.
- **Decision impact:** Forces explicit provenance, validates endpoints before mutation, and makes updates idempotent by source URI.

## Shape
```json
{
  "schema_version": "graph-patch-v1",
  "source": {"uri": "repo://demo/src/auth.py", "kind": "code", "content_hash": "sha256:...", "metadata": {}},
  "nodes": [
    {
      "id": "file:src/auth.py",
      "kind": "file",
      "label": "auth.py",
      "aliases": ["auth"],
      "properties": {},
      "evidence": [{"provenance": "EXTRACTED", "confidence": 1.0, "locator": "L1-L40", "status": "accepted", "details": {}}]
    }
  ],
  "edges": []
}
```

## Evidence vocabulary
`provenance` is one of:
- `EXTRACTED` — explicitly present in deterministic source syntax/data.
- `DERIVED` — computed mechanically from accepted graph/source data.
- `INFERRED` — model/heuristic interpretation that is not explicit.
- `MANUAL` — deliberate human/user assertion.

`status` is `accepted`, `ambiguous`, `rejected`, or `stale`. Confidence is numeric `[0,1]`; it is evidence strength, not probability of universal truth.

## Rules
- Every node and edge in a patch needs at least one evidence row.
- Edge endpoints must exist already or be included in the same patch.
- Keep `properties` JSON-compatible and small; large source bodies belong outside the graph.
- Use one source URI for one independently refreshable evidence unit. File-level sources are usually safer than treating an entire repository as one source.
- Use source `content_hash` when available so callers can skip unchanged sources.
- Do not smuggle secrets or raw sensitive payloads into `properties`/`details` as a convenience.
