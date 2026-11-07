# Trace export

Use normalized JSON only where the user's agent history export is available with permission. Store traces outside the target repository; they can contain private code and prompts. The script in an Archify checkout accepts `--trace-export path/to/trace.json`.

Expected top-level shape: `schemaVersion: 1`, `sessions: []`; each session has `id` and ordered `messages`. Normalize tool calls to `read` with `{ "file_path": "..." }`, `write` with `{ "file_path": "...", "content": "..." }`, and `exec` with `{ "command": "..." }`. Preserve tool responses and failures with their actual `tool_call_id`; a first candidate created through patch/shell must have a corresponding source-content event. Session task must identify the actual round/type directory.

For example:

```json
{
  "schemaVersion": 1,
  "sessions": [{
    "id": "archify-run-1",
    "messages": [
      {"role": "user", "content": "Create a diagram in /absolute/round/workflow"},
      {"role": "assistant", "tool_calls": [{"id": "w1", "name": "write", "arguments": {"file_path": "/absolute/round/workflow/.archify/demo/candidate.json", "content": "{\"diagram_type\":\"workflow\"}"}}]},
      {"role": "tool", "tool_call_id": "w1", "content": "Written"}
    ]
  }]
}
```

The candidate JSON above is illustrative, not a valid full diagram. Never turn missing trace events into fabricated successful commands. Original contract: [trace-export.md](https://github.com/ginmp8/archify/blob/a4065941f12be7967436261d9934784e381d423c/.agents/skills/archify-tuning/references/trace-export.md).
