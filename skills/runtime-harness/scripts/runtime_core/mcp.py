"""Small read-only stdio MCP profile. No HTTP, writes, process launch or network."""
from __future__ import annotations
from . import VERSION
from .common import MAX_INPUT, RuntimeFault, canonical, strict_json
from .query import execute_query
from .store import Store

PROTOCOLS = ("2025-11-25", "2025-06-18")
QUERY_SCHEMA = {
    "type": "object", "required": ["operation"], "additionalProperties": False,
    "properties": {
        "operation": {"type": "string", "enum": ["status", "resolve", "context"]},
        "refs": {"type": "array", "minItems": 1, "maxItems": 32, "uniqueItems": True,
                 "items": {"type": "string", "minLength": 1, "maxLength": 1024}},
        "budget_bytes": {"type": "integer", "minimum": 128, "maximum": 65536, "default": 8192},
        "if_none_match": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
    "allOf": [{"if": {"properties": {"operation": {"const": "status"}}},
               "then": {"not": {"required": ["refs"]}}, "else": {"required": ["refs"]}}]
}
TOOL = {"name": "runtime_query", "description": "Resolve exact local runtime/resource IDs or request bounded context from an initialized workspace. Read-only; no discovery, installation, execution or permission transfer.",
        "inputSchema": QUERY_SCHEMA, "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}


def failure(id, code, message):
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


class Session:
    def __init__(self, store: Store):
        self.store = store
        self.initialized = False
        self.ready = False

    def handle(self, message):
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
            return failure(None, -32600, "Invalid JSON-RPC request")
        id = message.get("id")
        if "id" in message and (isinstance(id, bool) or not isinstance(id, (str, int))):
            return failure(None, -32600, "Invalid request id")
        method, params = message["method"], message.get("params", {})
        if "id" not in message:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        if not isinstance(params, dict):
            return failure(id, -32602, "Parameters must be an object")
        if method == "ping":
            return {"jsonrpc": "2.0", "id": id, "result": {}}
        if method == "initialize":
            version, caps, client = params.get("protocolVersion"), params.get("capabilities"), params.get("clientInfo")
            if self.initialized or not isinstance(version, str) or not version or not isinstance(caps, dict) or not isinstance(client, dict) or not isinstance(client.get("name"), str) or not isinstance(client.get("version"), str):
                return failure(id, -32602, "Invalid or repeated initialization")
            self.initialized = True
            result = {"protocolVersion": version if version in PROTOCOLS else PROTOCOLS[0],
                      "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "rhapsodia-runtime", "version": VERSION}}
        elif not self.ready:
            return failure(id, -32002, "Initialize and send notifications/initialized first")
        elif method == "tools/list":
            if set(params) - {"cursor"} or params.get("cursor") not in (None, ""):
                return failure(id, -32602, "This fixed tool surface has no continuation cursor")
            result = {"tools": [TOOL]}
        elif method == "tools/call":
            if set(params) - {"name", "arguments", "_meta"} or params.get("name") != "runtime_query" or not isinstance(params.get("arguments"), dict):
                return failure(id, -32602, "Unknown tool or invalid arguments")
            try:
                data = execute_query(self.store, params["arguments"])
                is_error = False
            except RuntimeFault as exc:
                data, is_error = exc.result(), True
            except (OSError, UnicodeError):
                data, is_error = RuntimeFault("IO_ERROR", "Local resource unavailable.", 3).result(), True
            result = {"content": [{"type": "text", "text": canonical(data).decode("utf-8").rstrip("\n")}],
                      "structuredContent": data, "isError": is_error}
        else:
            return failure(id, -32601, "Method not found")
        return {"jsonrpc": "2.0", "id": id, "result": result}


def serve(store: Store, source, sink) -> int:
    session = Session(store)
    while True:
        line = source.readline(MAX_INPUT + 1)
        if not line:
            return 0
        if len(line) > MAX_INPUT:
            sink.write(canonical(failure(None, -32600, "Message exceeds the bounded stdio frame size")))
            sink.flush()
            return 2
        try:
            message = strict_json(line)
        except RuntimeFault:
            response = failure(None, -32700, "Parse error")
        else:
            response = session.handle(message)
        if response is not None:
            sink.write(canonical(response))
            sink.flush()
