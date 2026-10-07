# Local access without an external application

## CLI and Python
The main path is a local subprocess, `scripts/graph.py`, returning JSON. Imported modules may be used by another trusted Python program. Input/output contracts are host-neutral; use absolute resolved package/database paths rather than assuming a working directory.

## Local read-only HTTP
`... --db graph.db serve --viewer graph.html --port 8765` is explicitly started in the foreground and binds only 127.0.0.1. It serves the chosen local viewer, not an arbitrary source directory. A process-local capability token is inserted into the page; same-origin, Host and custom-header checks protect the query endpoint. Logs avoid payloads/tokens. No CORS, remote bind, arbitrary SQL, filesystem browsing, uploads or graph mutations are exposed.
The live query panel sends typed requests to the same local server only on user action. Static HTML remains useful without this server and cannot silently read a disk database. The local HTTP service is a bundled optional mode, not an external app dependency or a production multi-user web service.
Keep the generated viewer trusted. A reviewed local G6 bundle is executable code and therefore a separate trust decision. The local token is not an enterprise authentication/authorization system.

## Local stdio MCP
`... --db graph.db mcp` implements a bounded read-only MCP profile over newline-delimited JSON-RPC on stdin/stdout. It supports initialization/version negotiation, initialized notification, ping, tools/list and tools/call for `local_graph_query`. Diagnostics never pollute stdout. Tool results include text and structuredContent; domain failures are marked isError.
Protocol baseline is 2025-11-25 with an explicitly supported 2025-06-18 negotiation value. Only advertised tools are available. No HTTP MCP, writes, sampling, resources, tasks, OAuth, external model or arbitrary shell/SQL tool. Requests are synchronous and bounded; there is no claim of full protocol conformance or asynchronous cancellation across every host.
A host can launch Python with arguments `["/path/graph.py","--db","/path/graph.db","mcp"]`. The exact host configuration wrapper varies; keep it outside the semantic core. A chat that cannot launch local processes cannot access the user's local filesystem through this package.

## Safe capabilities
Do not auto-start a server or MCP process merely because its code is present. User-requested local viewing/access is the authorization to start the corresponding foreground process. Stop it when finished. Missing tools or unsupported clients are capability limits, not permission to bypass host policy.
