# Reproducibility and portability

## At a Glance
- **Purpose:** Control avoidable rendering variance and define offline/multi-host behavior.
- **Load when:** Comparing HTML hashes, packaging, changing dependencies, or making portability claims.
- **Decision impact:** Fixes version pins, layout selection, serialization, and evidence ceilings.

## Controls
- GraphView and viewer config are JSON-serialized with sorted keys.
- No wall-clock timestamp is injected into generated HTML.
- Automatic layouts avoid force; force requires explicit selection.
- Kind colors derive from stable string hashing.
- Template, input GraphView, backend, selected layout, and optional local G6 bundle fully determine output bytes.
- Python stdlib is the only required generation runtime.
- `--backend builtin` is self-contained/offline. `--backend auto|g6` uses G6 when the pinned bundle loads and otherwise falls back to builtin. `--g6-js` removes the CDN dependency while retaining G6.

Package structure can be statically compatible with multiple Agent Skills hosts, but browser/G6 runtime behavior is only `validated` where actually executed.
