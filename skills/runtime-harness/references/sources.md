# Primary sources and implementation boundaries

Reviewed 2026-10-07. These references informed host/protocol adapters, not measured
performance claims. User-supplied RhapsodIA 0.6.0 source is authoritative for existing
agent ownership, handoff, packaging and skill boundaries.

- Python isolated/no-site CLI: https://docs.python.org/3/using/cmdline.html
- Python which/current-directory behavior: https://docs.python.org/3/library/shutil.html#shutil.which
- Python subprocess and argv: https://docs.python.org/3/library/subprocess.html
- Python virtual environments: https://docs.python.org/3/library/venv.html
- MCP stdio transport (supported baseline): https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- MCP lifecycle/version negotiation: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle
- MCP tools/structured output: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- VS Code Local hooks and host differences: https://code.visualstudio.com/docs/agent-customization/hooks
- VS Code Local SessionStart output: https://code.visualstudio.com/docs/agents/reference/hooks-reference
- GitHub repository instructions: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- Cursor rules: https://cursor.com/docs/rules
- GitHub Actions setup-python: https://github.com/actions/setup-python
- GitHub Actions checkout: https://github.com/actions/checkout

The supported MCP profile deliberately does not claim a speculative 2026 protocol
upgrade. VS Code Local hooks are a host-specific, preview surface; the portable
runtime is independent of hook availability. No host runtime is considered validated
merely because its instruction filename is generated.

## Additive 1.2.0 verification (2026-10-08)

- https://modelcontextprotocol.io/specification/2026-07-28/server/discover
- https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning
- https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching

Modern per-request metadata and private discovery/list caching are implemented only in
the selected stdio profile. Legacy initialization behavior remains separately supported.
