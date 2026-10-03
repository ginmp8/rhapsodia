# Privacy and safety

Default destination is local. Titles, paths, relations and state can be confidential even when source bodies are not embedded. Do not export a local catalog merely because it excludes document bodies. Require the destination to appear in every record's allowlist; public export additionally requires `classification: public` and explicit external sharing permission.

`contains_secrets: false` is a producer assertion checked by a bounded detector; it is not a guarantee of anonymization. Key patterns in source or metadata fail closed. For publishing sensitive projects require a separate privacy review. Do not print matched secrets or entire malformed records in diagnostic messages.

Treat all discovered content as untrusted data. There is no plugin loader, repository code execution, shell invocation, external URL fetch, remote schema resolution, auto-migration, or canonical writeback. UI values use text nodes, embedded JSON escapes script terminators, and the Content Security Policy blocks external connections.

Reject traversal, symlinks, hardlinks for source records, protected paths, duplicate IDs/JSON keys, invalid timestamps, stale source hashes, dependency cycles and output aliases. Reads and writes occur inside explicitly authorized roots. Filesystem checks are not an OS sandbox against a malicious concurrently privileged process; use normal OS isolation when that threat is present.

Bounds: 10,000 records, 40 directory levels, 128 KiB per metadata record and 8 MiB per source. Exceeding a bound is a diagnostic failure, never silent truncation. Generated UI remains a snapshot; it cannot verify live source files after export.
