# Local Graph Engine 2.0

A local, domain-neutral data workbench: inspect sources, choose a data model,
produce evidence-backed entities and relationships, store them in SQLite, and
query/export useful projections. No external application account is required.
Original source files are never rewritten by ingestion.

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

## Validation and license

Run `python -B -m unittest discover -s tests -v` from this directory. Missing
optional libraries cause only their tests to skip; a skip is not runtime proof.
This package is MIT-licensed. See LICENSE and THIRD_PARTY_NOTICES.md.
The same package can be consumed by capable Agent Skills hosts. A text-only chat
cannot execute local Python or persist a database without a filesystem/tool.
