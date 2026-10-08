"""Actual newline-delimited stdio exchanges; not a claim of full MCP conformance."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "scripts/runtime.py"


def init(version="2025-11-25"):
    return {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": version, "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}}


def ready():
    return {"jsonrpc": "2.0", "method": "notifications/initialized"}


def rpc(id, method, params=None):
    result = {"jsonrpc": "2.0", "id": id, "method": method}
    if params is not None:
        result["params"] = params
    return result


class McpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="runtime mcp ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        result = subprocess.run([sys.executable, "-S", "-B", str(CLI), "--workspace", str(self.root), "init"], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def exchange(self, messages=None, raw=None, expected=0):
        if raw is None:
            raw = b"".join((json.dumps(v) + "\n").encode() for v in messages)
        proc = subprocess.run([sys.executable, "-S", "-B", str(CLI), "--workspace", str(self.root), "mcp"], input=raw, capture_output=True, timeout=15)
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        self.assertNotIn(b"Traceback", proc.stderr)
        return [json.loads(line) for line in proc.stdout.splitlines()]

    def test_initialize_list_call_and_no_notification_response(self):
        responses = self.exchange([init(), ready(), rpc(2, "tools/list"), rpc(3, "tools/call", {"name": "runtime_query", "arguments": {"operation": "resolve", "refs": ["tool://python"]}})])
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0]["result"]["protocolVersion"], "2025-11-25")
        tools = responses[1]["result"]["tools"]
        self.assertEqual([tool["name"] for tool in tools], ["runtime_query"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        result = responses[2]["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(json.loads(result["content"][0]["text"]), result["structuredContent"])

    def test_missing_initialization_is_rejected(self):
        r = self.exchange([rpc(4, "tools/list")])
        self.assertEqual(r[0]["error"]["code"], -32002)

    def test_legacy_version_is_negotiated(self):
        r = self.exchange([init("2025-06-18"), ready(), rpc(2, "tools/list")])
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-06-18")

    def test_unknown_version_returns_supported_version(self):
        r = self.exchange([init("1900-01-01")])
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-11-25")

    def test_write_method_and_unknown_tool_rejected(self):
        r = self.exchange([init(), ready(), rpc(2, "runtime/init"), rpc(3, "tools/call", {"name": "shell", "arguments": {}})])
        self.assertEqual(r[1]["error"]["code"], -32601)
        self.assertEqual(r[2]["error"]["code"], -32602)

    def test_bad_arguments_are_tool_errors(self):
        r = self.exchange([init(), ready(), rpc(2, "tools/call", {"name": "runtime_query", "arguments": {"operation": "execute"}})])
        self.assertTrue(r[1]["result"]["isError"])
        self.assertEqual(r[1]["result"]["structuredContent"]["error"]["code"], "INVALID_INPUT")

    def test_invalid_json_and_utf8_are_parse_errors(self):
        r = self.exchange(raw=b'{not json}\n\xff\n')
        self.assertEqual([v["error"]["code"] for v in r], [-32700, -32700])

    def test_oversized_message_stops_bounded_stream(self):
        r = self.exchange(raw=b"x" * 65538 + b"\n", expected=2)
        self.assertEqual(r[0]["error"]["code"], -32600)

    def test_batch_and_boolean_ids_are_rejected(self):
        r = self.exchange([[], {"jsonrpc": "2.0", "id": True, "method": "ping"}])
        self.assertTrue(all(v["error"]["code"] == -32600 for v in r))

    def test_required_initialized_notification(self):
        r = self.exchange([init(), rpc(2, "tools/list")])
        self.assertEqual(r[1]["error"]["code"], -32002)

    def test_ping_before_init_and_unknown_notification(self):
        r = self.exchange([rpc(2, "ping"), {"jsonrpc": "2.0", "method": "notifications/unrecognized"}])
        self.assertEqual(r, [{"jsonrpc": "2.0", "id": 2, "result": {}}])


if __name__ == "__main__":
    unittest.main()
