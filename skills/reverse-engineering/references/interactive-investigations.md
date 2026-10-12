# Persistent investigations: offline graph, evidence, and MCP

**Purpose:** reconstruct what a source tree or packaged application *declares* and retain bounded, queryable evidence without running it.
**Load when:** analyzing Electron, JS/TS, ASAR, ZIP/TAR, Apple bundles, binary metadata, or using the optional MCP/CLI server.
**Decision impact:** defines scope, parser ceilings, persistent identifiers, replay/receipt trust, cancellation, and correct protocol/CLI use.

## Trust setup and invocation

- Python 3.10+ standard library. No project dependency resolution, target process, archive extraction, Node.js server, browser, network listener, shell action or extra package installation.
- Explicit existing `--root PATH` defines readable artifacts. Every analysis `path` is scoped to that root. No symlinks/traversals permitted, and member bytes/entry counts/decompression ratio are bounded. On POSIX with `openat` + `O_NOFOLLOW`, directory reads keep components pinned; on unsupported operating systems the fallback is best-effort and sensitive roots require OS-level restrictions.
- Optional existing private `--state-dir PATH` retains `investigations.sqlite3` and is the *only* directory the MCP writes to (except standard process logs on stderr). Without it, evidence remains in-memory until process shutdown. Treat the state directory as sensitive: it contains paths and source-derived metadata. No server is a filesystem sandbox, and an attacker controlling the host can still access files permitted to this process.
- `--verifier-key-file PATH` is *only* a server-startup argument, never an MCP tool parameter. Supply an operator-owned raw secret of 32–512 bytes; on POSIX, permissions must deny group/other access. The workbench verifies HMAC signatures but never generates trusted execution receipts or stores the secret in SQLite.

Example CLI against a read-only snapshot (use actual platform Python command):

```sh
python3 -B scripts/mcp_server.py --root /approved/snapshots --state-dir /private/re-state --tool inventory_source --args-json '{"path":"app.asar","offset":0,"limit":100}'
python3 -B scripts/mcp_server.py --root /approved/snapshots --state-dir /private/re-state --tool analyze_application --args-json '{"path":"project.zip"}'
python3 -B scripts/mcp_server.py --root /approved/snapshots --state-dir /private/re-state --tool query_evidence --args-json '{"kind":"application_graph","limit":10}'
python3 -B scripts/mcp_server.py --root /approved/snapshots --state-dir /private/re-state
```

MCP clients launch the final command as a subprocess with stdin/stdout JSON-RPC. The server speaks modern `2026-07-28` per-request `_meta` and `server/discover`, or legacy `initialize` for the supported `2025-06-18` / `2025-11-25` profiles. Modern tool results include `structuredContent` and `resultType:"complete"`. `tools/list`, `resources/list|read`, `prompts/list|get`, and `ping` are supported; no Streamable HTTP listener, tasks, sampling, elicitation, reverse-host filesystem access, dynamic code execution or authorization proxy are implemented. The server processes one analysis at a time and has cancellation hints; cancellation does **not** interrupt an operation already running in the worker.

## Complete named tool inventory

| Tool | Inputs/operation | Evidence scope |
|---|---|---|
| `inventory_source` | `path`, `offset`, `limit`: bounded listing | Member paths/sizes, SHA-256 identity, exclusions; no content execution |
| `analyze_application` | `path`, `max_files`, `max_edges` | Static JS/TS/Electron imports, exports, routes and event/IPC candidates |
| `trace_application` | `evidence_id`, `query`, `direction`, `depth`, `max_nodes` | Traversal of saved candidate graph, no resolved runtime dispatch |
| `compare_applications` | `before_evidence_id`, `after_evidence_id` | Hash/edge/role changes, not behavior equivalence |
| `inspect_artifact` | `path`, optional `member`, `mode` | Bounded binary metadata and built-in format subset |
| `inspect_apple_bundle` | `path` | Declarative `.app`/plist metadata from bounded artifact members |
| `query_evidence` | `kind`, `artifact_sha256`, paging | Stable SQLite evidence references |
| `inspect_evidence_view` | `evidence_id`, `section`, paging | `summary`, `nodes`, `edges`, `items`, `unknowns` and available sections |
| `export_evidence_bundle` | `filename` | No overwrite; content hash and bundle hash; destination state root |
| `import_evidence_bundle` | `path` | Integrity validation, atomic insert; importing cannot elevate evidence tier |
| `build_reconstruction_ledger` | `graph_evidence_id`, `obligations`, `bindings`, `verification_records` | Required obligations, fixture partitions, verified finite receipts, blockers |
| `compare_partial_order` | `reference`, `candidate` | DAG payload IDs/reachability independent of unrelated interleaving |
| `detect_capabilities` | none | Actually bundled adapter families, optional external boundaries |

Every MCP tool uses a typed JSON Schema with `additionalProperties:false`. Static inspection uses source identity hashes and a bounded ledger. Query the retained record using the `evidence_id` returned by analysis. Large records stay in SQLite; request individual sections/pages rather than asking the model to ingest whole codebases.

## Reconstruction receipt: authenticated metadata, not executable authority

- First freeze source/candidate hashes, observation corpus, test environment and reset state in a separately approved verifier. Generate case expectations by observing an authorized reference; never guess from static code.
- An obligation has `obligation_id`, `title`, `required`, `required_case_kinds`, `authority_sha256` (frozen reference SHA-256) and optionally `needs_review`/`dependencies`.
- One binding per obligation requires `obligation_id`, `owner`, `contract_type`, `candidate_sha256` (implementation identity), and `fixtures` mapping required case kinds to existing fixture IDs.
- Each trusted receipt includes `obligation_id`, `authority:"trusted_runtime_receipt"`, `result:"pass"`, `source_sha256`, `candidate_sha256`, `corpus_sha256` (all lowercase 64-hex), `cases` and a nonempty `recorder` identity. An independently authorized recorder canonicalizes *these fields* (sorted compact JSON, UTF-8, no NaN), calculates `receipt_sha256 = SHA256(canonical_payload)` and `attestation_hmac_sha256 = HMAC-SHA256(operator_secret, canonical_payload)`. The verifier excludes these two digest fields from the canonical payload. The operator, not model/tool arguments, provisions the secret file for the workbench.
- No secret, no matching hashes, incomplete case partitions, conflicting failures, unresolved unknown, unchecked hypotheses or missing fixture/owner => `incomplete` or `unknown`. Even signed `ready` proves only matching finite recorded cases, assuming trust in the independent recorder and its environment. Do not equate signature with attestation of physical isolation or source equivalence.

## Offline results and limits

- Archive: 384 MiB input maximum, 12,000 entries, 16 MiB per member, 96 MiB accumulated readable member sizes. ASAR unpacked and linked entries are excluded; unsupported ASAR Pickle variations are reported rather than guessed. TAR/ZIP entries are never extracted.
- Graph: lexical JS/TS route/import/IPC patterns. Comment masking is not semantic name resolution, computed dynamic imports, secure source map restoration or cross-language call tracking. Edge and node budgets enforce partial reports. External encodings and malformed files may be excluded.
- PE resource: parse bounded leaf metadata and SHA; ELF/core: bounded program-header and note metadata; Apple Info.plist: declared keys only. None is a general disassembler, Mach-O crash unwinder or automatic source recovery.
- SQLite import/export: hash checking catches accidental/detectable tampering without secret-origin attestation. Imported assertions remain untrusted supplied content. Do not present completeness unless `complete` is true *for recognized constructs* and explicit unknowns/skip counts are zero.
- Strict partial-order events have unique IDs, JSON payloads, `before` predecessor lists and finite reachability; cycles and unresolved predecessors fail closed. The comparator judges exactly that event graph, not every possible concurrency schedule or happens-before behavior in a live program.
