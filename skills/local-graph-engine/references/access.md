# Local access without an external application

## CLI and Python
The main path is a local subprocess, `scripts/graph.py`, returning JSON. Imported modules may be used by another trusted Python program. Input/output contracts are host-neutral; use absolute resolved package/database paths rather than assuming a working directory.

## Local read-only HTTP
`... --db graph.db serve --viewer live.html --port 8765` is explicitly started in the foreground and binds only 127.0.0.1. Version 3 requires a reviewed local-live HTML runtime v1 artifact; a compatible producer can generate it (Explorer uses `--security-profile local-live`). Offline, extended and legacy custom pages fail closed rather than receiving a database capability.

Add `--viewer-sha256 <SHA256_FROM_RENDER_RECEIPT>` to pin the exact artifact. The server validates UTF-8, early CSP, profile/version, the empty inert session slot and every inline script hash before binding. It serves only that in-memory snapshot and never rewrites the disk HTML or authorizes all inline scripts. See [live contract](live-viewer-contract.md) for trust limits and migration.

The session is JSON data, not injected executable JavaScript. Exact Host, optional Origin, Fetch Metadata and constant-time token checks protect the endpoint; duplicate authority headers are denied. Typed queries require JSON, a bounded Content-Length and no Transfer-Encoding. There is no CORS, redirect, remote bind, arbitrary SQL, directory browsing, upload or graph mutation. Headers prevent cache/referrer/framing; logs omit payloads/tokens.

Live queries occur only after user action. Client code must derive the URL from location.origin, use same-origin mode, reject redirects and omit ambient credentials/referrer. Snapshots need no listener. This local capability is not enterprise authentication and does not protect against malicious same-user processes or an untrusted selected HTML producer.

## Local stdio MCP
`... --db graph.db mcp` implements a bounded read-only MCP profile over newline-delimited JSON-RPC on stdin/stdout. It supports initialization/version negotiation, initialized notification, ping, tools/list and tools/call for `local_graph_query`. Diagnostics never pollute stdout. Tool results include text and structuredContent; domain failures are marked isError.
Protocol baseline is 2025-11-25 with an explicitly supported 2025-06-18 negotiation value. Only advertised tools are available. No HTTP MCP, writes, sampling, resources, tasks, OAuth, external model or arbitrary shell/SQL tool. Requests are synchronous and bounded; there is no claim of full protocol conformance or asynchronous cancellation across every host.
A host can launch Python with arguments `["/path/graph.py","--db","/path/graph.db","mcp"]`. The exact host configuration wrapper varies; keep it outside the semantic core. A chat that cannot launch local processes cannot access the user's local filesystem through this package.

## Safe capabilities
Do not auto-start a server or MCP process merely because its code is present. User-requested local viewing/access is the authorization to start the corresponding foreground process. Stop it when finished. Missing tools or unsupported clients are capability limits, not permission to bypass host policy.
