# Host Adapters

Keep `agent-design-contract/v2` as the portable semantic core. Host adapters map capabilities, artifact formats, tool names, and control-flow primitives without changing mission, authority, context, state, or validation semantics.

## Adapter Rules

1. Design semantic capabilities first (`repository-read`, `repository-search`, `filesystem-write`, `process-execute`, `network-access`, `mcp:<capability>`, `delegate:<role>`, etc.).
2. Resolve the current host's actual tool names and defaults before generating runnable frontmatter/configuration.
3. For read-only/review/router/governance roles, use explicit restrictive exposure. Do not assume omitted tool configuration means no tools.
4. If host semantics are unknown or current documentation/repository conventions are unavailable, emit a portable agent spec and mark host adaptation `blocked/not-verified` rather than inventing fields.
5. Host permissions and downstream authorization remain authoritative. Adapter metadata cannot grant permission the environment does not provide.
6. Keep host-specific paths/frontmatter out of portable references/templates unless clearly labeled as examples.

## Control-Flow Mapping

Map host behavior to one of the portable kinds:

- `delegate-return`: parent/manager retains top-level ownership; specialist returns a bounded result;
- `transfer-control`: recipient becomes the active/top-level owner for the transferred task/turn until another explicit transition;
- `suggested-transition`: host UI suggests another agent; no control transfer occurs until the user/host accepts it;
- `parallel-child`: parent retains orchestration ownership while children execute independent bounded work concurrently.

Do not call all four "handoff" without recording the kind.

## Host Notes

### OpenAI Agents SDK

- Map `Agent.as_tool(...)` style manager/specialist work to `delegate-return`.
- Map SDK handoffs that change the active agent to `transfer-control`.
- Keep authorization checks before side effects; context filters do not replace authority checks.

### GitHub Copilot custom agents

- `tools` controls exposed tools, including configured MCP tools.
- Omitted `tools` can expose all available tools; `tools: []` disables tools. For restricted roles, emit an explicit tool list.
- Product-specific tool aliases are adapter data, not portable capability names.

### VS Code custom agents

- `.agent.md` is a host artifact; use repository/user conventions when known.
- VS Code handoff buttons are typically `suggested-transition` semantics: the response completes and the UI offers switching agents with context/prompt.
- Keep semantic routing ownership separate from the presence of a UI button.

### Visual Studio

- Use current Visual Studio/Copilot agent-file conventions when detected.
- Tool names can differ from other Copilot surfaces; resolve them rather than copying a VS Code list blindly.
- Preserve the same portable authority/context/control-flow contract.

### Cursor

- Subagents normally behave as `delegate-return`: each has a separate context and returns results to the parent.
- Subagents may inherit parent tools, including MCP capabilities; explicit child authority must therefore be checked against actual inherited exposure.
- Parallel writers sharing a checkout can conflict. Require isolated workspaces/worktrees or another concurrent-mutation strategy.

### Claude

- Preserve the portable agent contract and adapt only from current host/repository conventions that are actually available.
- Do not assume Copilot/Cursor frontmatter or tool names apply to Claude.
- Keep Skill package semantics independent from any Claude-only agent configuration.

### Codex

- Preserve the portable agent contract and map capabilities to the current Codex execution surface only when available.
- Do not make Codex-specific paths/tool identifiers part of the core package.

## Structural Portability vs Runtime Portability

A package may be structurally portable while a generated agent artifact still requires host adaptation. Report separately:

- portable contract validity;
- host artifact validity;
- tool/capability exposure verified or unknown;
- runtime behavior executed or not-run.

Never infer runtime permission or behavior from portable Markdown alone.
