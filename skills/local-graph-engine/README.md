# Local Graph Engine 3.1.0

A local, domain-neutral data workbench: inspect sources, choose a data model,
produce evidence-backed entities and relationships, store them in SQLite, and
query/export useful projections. No external application account is required.
Original source files are never rewritten by ingestion.

## Persistent workspace memory

Rhapsodia profiles require graph-first memory unless the user explicitly opts out. This
mode initializes missing state, reuses fresh references, learns bounded source-pinned
knowledge and sanitized environment recipes, and reconciles changes without treating
partial search as deletion proof. It does not run commands found in records. The goal is to preserve structural knowledge and
operational experience across sessions, so the next investigation can reuse verified work.
Retrieve compact relevant context; learn only actionable nonduplicate findings. No useful new
finding means an explicit no-new-knowledge reason, not a filler write. Source/live evidence
and fresh validation remain necessary. Learned experiences may not be reconstructible after
a reset; preserve them separately from rebuildable source indexes.

```text
python -I -S -B scripts/workspace_memory.py --workspace <ROOT> start
python -I -S -B scripts/workspace_memory.py --workspace <ROOT> lookup "configuration loader"
python -I -S -B scripts/workspace_memory.py --workspace <ROOT> pin src/config.py
python -I -S -B scripts/workspace_memory.py --workspace <ROOT> learn --input <REVIEWED_NOTE_JSON>
python -I -S -B scripts/workspace_memory.py --workspace <ROOT> reconcile --paths src/config.py
```

Use actual source pins; do not copy placeholder paths into a completed record.
See [learning criteria](references/workspace-learning.md) for what to retain and why.
See [workspace memory](references/workspace-memory.md) for exact schemas, statuses,
concurrency, permissions and privacy. Standalone dataset workflows below remain unchanged.

## Start with a working example

From this skill directory, using an available Python 3.10+ launcher:

```text
python scripts/graph.py doctor
python scripts/graph.py --db demo/graph.db ingest examples/people.csv --mapping examples/people-mapping.json
python scripts/graph.py --db demo/graph.db validate-db
python scripts/graph.py --db demo/graph.db query examples/query-people.json
python scripts/graph.py --db demo/graph.db export json demo/graph-view.json
```

Send `demo/graph-view.json` to Local Graph Explorer or another GraphView consumer.
No network or third-party Python library is needed for this example.

## Bring your own data

```text
python scripts/graph.py inspect data.csv
python scripts/graph.py model data.csv --namespace my-dataset --output mapping.json
```

Review the proposed mapping before ingestion. Add explicit relation mappings when
columns actually establish a relationship. Choose a separate namespace for
unrelated identity domains and source roots; reuse one only for intentionally
shared identities. Sources with the same namespace and basename replace the
same dataset source; choose distinct namespaces when they are different datasets.
Do not silently infer joins just because names look similar.

## Capability and access

Read `references/capabilities.md` for native versus optional features and exact
runtime limitations. `references/queries.md` covers typed queries. Local HTTP
and stdio MCP are opt-in; they are not required by CLI or HTML exports.
Run `python scripts/graph.py --help` for all commands.


## Budget the agent context

Use `query examples/query-context.json` after the people import for compact evidence; use `query-context-evidence.json` only when details/properties matter. The additive `context` operation supports exact UTF-8 budgets, deterministic neighborhoods and explicit caller-held receipt reuse. See [context efficiency](references/context-efficiency.md) for fields, scope and the difference between bytes and estimated tokens.

```text
python scripts/graph.py --db demo/graph.db query examples/query-context.json
python scripts/measure_context.py --db demo/graph.db --request examples/query-context.json
```

No LLM, tokenizer download, hidden cache or reference-project dependency is introduced. The compact envelope is not GraphView; export GraphView separately for visualization.

## Validation and license

Run `python -B -m unittest discover -s tests -v` from this directory. Missing
optional libraries cause only their tests to skip; a skip is not runtime proof.
This package is MIT-licensed. See LICENSE and THIRD_PARTY_NOTICES.md.
The same package can be consumed by capable Agent Skills hosts. A text-only chat
cannot execute local Python or persist a database without a filesystem/tool.

## Version 3 local-access migration

Offline database/query/context operations keep their commands and data formats.
For HTTP, regenerate a native **local-live HTML runtime v1** artifact; an old
offline or custom HTML is not automatically granted database access. A compatible
Explorer uses `render view.json --output live.html --security-profile local-live`.
Then start the foreground server explicitly:

```text
python scripts/graph.py --db graph.db serve --viewer live.html --port 8765 --viewer-sha256 <SHA256_FROM_RENDER_RECEIPT>
```

The expected hash is optional but recommended for binding the reviewed artifact.
A matching hash alone does not prove trust. See [local access](references/access.md)
and the [HTML trust contract](references/live-viewer-contract.md). No database,
GraphView or context migration and no new required library is introduced.
