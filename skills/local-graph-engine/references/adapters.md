# Source adapters and coverage

## Record sources
`inspect`, `model` and `ingest` read CSV, TSV, JSON object/array, JSONL/NDJSON, simple XML records and ordinary SQLite tables with Python stdlib. CSV delimiter/header selection is explicit or sniffed from a bounded sample; malformed rows/duplicate headers fail. XML forbids DTD/entity declarations. SQLite uses read-only ordinary-table access and requires `--table` when ambiguous.
Use `--records-path` for a JSON nested record collection or XML record selector. `--header-row` handles an explicitly identified leading header offset. No automatic recovery of unknown malformed encodings/headers is claimed. Default input limit is 32 MiB and 100,000 rows; split larger datasets deliberately.
XLSX uses installed openpyxl (read-only, formulas are data, no external links); YAML uses installed PyYAML safe_load. Missing dependencies fail with an explicit capability message. No library is installed implicitly.
`ingest --structural` accepts arbitrary finite JSON and emits object/array/value containment with JSON-pointer evidence. It does not invent business relationships.

## Folder and document scan
`scan folder --namespace study [--code-backend builtin|tree-sitter]` is bounded by file count and size; skip symlinks, secrets, dependency/build/output directories. Inspect coverage/skipped/error receipts. Extraction failures prevent the batch commit; explicit skips remain visible. Outputs must not alias or live inside the scanned source tree.
Text/Markdown/HTML/DOCX yield structural source, heading and link relationships, not automatic semantic knowledge. HTML script/style content is ignored. DOCX uses bounded ZIP/XML reading; macros are never run. PDF text uses installed pypdf; image-only pages require a separate image/vision/OCR capability and are not silently treated as complete.
Python uses stdlib AST for definitions/imports/call sites. A possible call target is labeled inferred/ambiguous unless semantically established. Other code defaults to file inventory; explicit Tree-sitter mode needs tree_sitter_language_pack and provides syntax structure, not compiler-level resolution.
The optional C# source adapter under adapters/roslyn uses locally installed .NET compiler assemblies. It never builds the inspected project or executes its hooks. Its exact scope/limitations and unexecuted delivery checks are documented in its README.

## Other deterministic inputs
`schema database.sqlite --namespace data` extracts local table/column/foreign-key structure. `openapi api.json --namespace api` extracts OpenAPI JSON endpoints/schemas/references. Neither connects to a remote production system.
`git repository --namespace repo --max-commits 100` requires installed Git and reads local history/changed paths/parents without installing hooks or storing author email. It does not retrieve GitHub PR state.
`import-graphml file.graphml --namespace graph` accepts one ordinary GraphML graph with explicit direction. Nested graphs/hyperedges require a declared relationship-node mapping. GraphPatch retains repeated edge observations, not distinct canonical event identities.

## Optional local speech and agent interpretation
`transcribe audio.wav --namespace audio --model-dir /local/whisper-model` requires installed faster-whisper and a supplied local model. Downloads are disabled. Transcript text is model-derived/uncertain, not ground-truth speech. Model weights/license/hardware are the user's explicit choice. No bundled ASR weights or codec binaries.
For images, scanned pages, arbitrary media, exported messages or business semantics, use an available host vision/document capability or an explicitly selected open-source extractor, then emit GraphPatch with locators and provenance. This is an agent workflow, not a claim of a universal built-in parser.
Never require an external application merely to import its data: request a local export when a connector/account is absent. Authenticated live connectors, OAuth and provider-specific applications are not core dependencies.

## Refresh and watching
`watch` is explicitly invoked, foreground, interval-bounded and iteration-bounded (default three passes). It does not register a daemon, schedule background work or install Git hooks. Changed source assertions replace their previous versions; identical normalized patches are skipped. `--prune-missing` explicitly tombstones missing source URIs in that namespace; never enable it without understanding the scan boundary.
