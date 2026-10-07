# Capability inventory

## Delivered standard-library core
Data profiling; reviewed domain mapping; CSV/TSV/JSON/JSONL/simple XML/SQLite records; structural JSON; Markdown/HTML/text/DOCX structure; Python AST; local SQLite schema; OpenAPI JSON; GraphML import; atomic graph patches; full source claims/revisions; bounded queries/search/SQL; components/SCC/degree/PageRank; typed aggregates/timelines/quality; source history/restore; namespace federation; GraphView/GraphML/DOT/Mermaid/CSV/wiki; backup; saved queries; outcome memory; foreground bounded watching; local read-only HTTP; bounded stdio MCP profile.
These are implemented local mechanics. Semantic interpretation of arbitrary documents/images remains agent-assisted and must be evidenced; file inventory is not semantic extraction.

## Optional open-source capabilities
| Capability | Requires | Delivery evidence |
|---|---|---|
| XLSX records | openpyxl | Runtime covered by optional test in available environment. |
| YAML records | PyYAML | Runtime covered by optional test in available environment. |
| Rich graph algorithms | NetworkX | Greedy communities tested; per-algorithm capability checked. |
| PDF text | pypdf | Adapter included; PDF runtime coverage stated in validation report. |
| Non-Python syntax | tree_sitter_language_pack | Code included, dependency unavailable in delivery environment. |
| C# static semantics | installed .NET 10 SDK | Source adapter included, compile/runtime not-run. |
| Local Git history | installed Git | Temp-repository integration tested. |
| Local speech | faster-whisper + explicit local model | Code included, model/runtime not-run. |
| Local G6 rendering | reviewed G6 UMD bundle | Explorer integration included, G6 runtime not-run. |

No optional dependency is silently installed. Use `doctor` to discover available capabilities. The tested environment is an evidence record, not a recommendation to pin outdated versions forever. Freeze and validate a compatible dependency set when distributing optional features.

## Intentionally no required external application
No Neo4j, FalkorDB, SaaS, vector server, login, cloud LLM, external API key, Docker or 21st.dev runtime. Data exports from another system are valid inputs; accessing live authenticated systems still requires their authorization/tooling. Local libraries and general-purpose Python/browser/compiler runtimes are not application accounts.
PR dashboards, enterprise auth, continuous hosted monitoring, arbitrary image OCR and universal source execution are not disguised as completed native capabilities. Their supplied data can be modeled/imported, or a capability adapter can produce GraphPatch. User-controlled extension is possible without weakening the evidence boundary.

## Agent context (2.1)
Compact/evidence contexts, exact serialized-byte limits, deterministic bounded neighborhoods, deduplicated source locators, explicit caller-held reuse and same-selection byte comparison are standard-library mechanics. Real tokenizer counts, retrieval relevance/answer-quality evaluation and implicit persistent caches are not claimed. Existing HTTP/MCP surfaces expose context without granting write authority.
