# Bounded read-only, dual-era MCP profile

Start `<PYTHON> -I -S -B scripts/runtime.py --workspace <ROOT> mcp` after initialization.
Newline-delimited UTF-8 JSON-RPC over stdio only; no HTTP/listener. EOF terminates. Frames
are at most 64 KiB and stdout remains protocol-only. The one tool is `runtime_query`.

## Modern 2026-07-28

Each request includes `params._meta` with `io.modelcontextprotocol/protocolVersion` set
to `2026-07-28` and `io.modelcontextprotocol/clientCapabilities` as an object. No handshake
is required and modern requests do not modify legacy session state. `server/discover`
returns supported versions, tool capability and self-reported server information.

`server/discover` and `tools/list` return resultType complete, ttlMs 60000 and cacheScope
private. This caches stable discovery/catalog metadata, not live tool results. `tools/call`
and ping include resultType complete; tool calls have no cacheability hint. Missing modern
metadata is -32602; unsupported versions are -32022 with supported/requested data.
Modern methods: server/discover, ping, tools/list, tools/call. No unimplemented extension
or capability is advertised. This remains a narrow stdio profile, not a full-conformance
claim across every protocol method, transport, SDK or IDE.

## Legacy preserved

2025-11-25 and 2025-06-18 retain initialize plus notifications/initialized before tool calls.
Unknown initialize versions receive the preferred legacy supported version and the client
must decide compatibility. Modern calls can coexist without implicitly initializing legacy.
Older handoff/query formats are unchanged. No speculative stateless HTTP adapter is added.

## Authority and measurement

Query paths never discover, write state, execute processes or authorize work. Missing or
stale state produces an error; an already-authorized worker refreshes explicitly. The
process assumes an authorized local client, not a multi-user authentication service.

Tool results include structuredContent and backward-compatible text. Application output_bytes
is not transport frame size or billed tokens. Whether a client places both representations
in the prompt must be measured there; this adapter does not silently remove compatibility.
No native IDE/client certification or actual token saving follows from local stdio tests.

Specifications: 2026-07-28 server/discover, basic/versioning, basic/transports/stdio,
server/tools and server/utilities/caching. URLs and retrieval date are recorded in sources.
