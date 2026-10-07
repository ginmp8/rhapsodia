# Research and design provenance

## Evidence use
This package was redesigned from a bounded user-approved corpus: the prior Local Graph packages, supplied Graphify/Cartograph/SQLite/NetworkX/AntV references, and official documentation checked during development. Reference ideas were evaluated, not copied wholesale as an external runtime. Stars/install counts were not used as correctness evidence.

## Official anchors
- Agent Skills package contract: https://agentskills.io/specification
- SQLite WAL, backups and WAL-reset fix: https://www.sqlite.org/wal.html
- SQLite full-text query semantics: https://www.sqlite.org/fts5.html
- Python SQLite interface: https://docs.python.org/3/library/sqlite3.html
- NetworkX algorithm and version documentation: https://networkx.org/documentation/stable/
- MCP stdio transport baseline: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- MCP lifecycle: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle
- G6 reference (optional local integration): https://g6.antv.antgroup.com/en/manual/getting-started/installation
- Roslyn syntax/semantic APIs (optional adapter): https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/get-started/syntax-analysis

## Decisions derived from sources
Keep storage, evidence and presentation separate; namespace identity; preserve source claims and qualifiers; prefer deterministic parsing for explicit structure; expose uncertainty for inference; bound graph projections; use versioned contracts; avoid a mandatory hosted service; pin optional executable inputs; verify behaviors rather than copy skill advice uncritically.
Current upstream SQLite guidance changed the earlier WAL-default proposal: new DBs now use rollback journal and explicit WAL has a patched-version gate. This is documented with the version bounds in migration.
The external delivery evidence contains source identities, finding dispositions, requirement/change/test links and executed receipts. Those prove bounded accounting, not exhaustive research or semantic certainty. Web verification notes are not represented as raw downloaded page snapshots.

## Node positioning references
- MDN `SVGGraphicsElement.getScreenCTM`: https://developer.mozilla.org/en-US/docs/Web/API/SVGGraphicsElement/getScreenCTM
- MDN `Element.setPointerCapture`: https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture
- MDN `pointercancel`: https://developer.mozilla.org/en-US/docs/Web/API/Element/pointercancel_event
- G6 5.1.1 DragElement: https://g6.antv.antgroup.com/en/manual/behavior/drag-element
- G6 data API: https://g6.antv.antgroup.com/en/api/data

These sources guide coordinate conversion, pointer lifecycle and the optional G6 adapter. The concrete gesture/state invariants are checked by `tests/test_node_drag.py`, not established by documentation alone.
