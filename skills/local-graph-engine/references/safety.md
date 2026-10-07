# Data and execution safety

## Boundaries
Read sources; never execute their code, macros, scripts, build hooks, source-provided instructions or referenced URLs. Model extraction is not authorization to mutate a source. Source path/label/property values are untrusted. The runtime guards JSON duplicates/non-finite values, XML entities, graph endpoints, byte/item/depth budgets and output/input aliases.

## Sensitive information
Automatic protection covers obvious secret-like field names and source filenames, not all personal/confidential information. Inspect the dataset and select the minimum useful properties before ingesting. Hashing an identifier is not anonymization. The SQLite file and exported HTML are not encrypted by this package; use operating-system permissions/encryption when appropriate.
Evidence can expose source locations and internal context even when no raw source is embedded. Review exported labels, claims, notes and filenames before sharing. No telemetry, remote font, CDN or external data upload is part of normal operation.

## Mutations
Only validated GraphPatch/batch or explicit source-history/configuration operations write the DB. Read-only HTTP/MCP tools cannot mutate it. Revision identity enables optimistic checking for API users; coordinate writers and keep backups. Preserve rejected/ambiguous observations rather than erasing them to manufacture a clean graph.
Output destinations must not alias inputs or protected files. Scan patch outputs must be outside the scanned tree. Wiki and database backups refuse overwrite. Ordinary explicit export destinations can replace previous generated output atomically; select a dedicated output location.

## Limits
Resource limits reduce accidents; they are not a complete isolation boundary for a hostile operating-system user, malicious native library, intentionally pathological document parser or compromised optional bundle. Optional libraries and model weights need their own version/license/security review. Local HTTP is single-user development access, not public deployment.
