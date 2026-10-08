# Bounded read-only MCP profile

Explicitly start `<PYTHON> -I -S -B scripts/runtime.py --workspace <ROOT> mcp` only after
initialization. The process uses newline-delimited UTF-8 JSON-RPC on stdio, no HTTP or
listener. EOF ends it. Diagnostics/errors remain protocol-safe. Request frames are
bounded to 64 KiB; oversized frames fail and terminate instead of buffering indefinitely.

Supported negotiated versions: `2025-11-25`, `2025-06-18`. An unsupported client version
receives the server's preferred supported version; the client must decide compatibility.
This is an explicitly bounded profile, not a latest-version or full-conformance claim.

Supported methods: `initialize`, `notifications/initialized`, `ping`, `tools/list`,
`tools/call`. Calls require the initialization handshake. There is exactly one tool,
`runtime_query`, with the same schema and read-only resolver as the CLI. No mutation,
bootstrap, command execution, arbitrary SQL, sampling, tasks, resources, OAuth or
network capability is advertised. Tool pagination is unnecessary for this fixed surface.

Tool results include `structuredContent` and backward-compatible text. Therefore the
query's `output_bytes` measures the canonical application JSON, not the larger MCP
message, duplicate text representation, client prompt, or billed tokens. Count those
at the host boundary for an end-to-end performance claim. No unsupported cache TTL or
stateless-HTTP extension has been added based on speculative protocol changes.

The MCP process does not refresh state implicitly. Missing/stale state returns a
structured tool error; the authorized bootstrap owner refreshes once and retries.
`mcp-config` prints argv only and never edits a client configuration or starts a server.
The local stdio profile assumes an already authorized client launched it; it is not a
multi-user authentication service. Primary specifications: [sources](sources.md).
