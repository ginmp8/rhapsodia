# MCP Security Profile

Use this optional profile only when the reviewed system materially uses Model Context Protocol. It augments `llm-agent-governance-review`; it is not a core dependency of the skill.

## Resolve the MCP shape first

Identify client, MCP server, authorization server/resource server roles, transport (`stdio`, HTTP/streamable HTTP, or other), tools/resources/prompts exposed, downstream APIs, credentials/tokens, and whether the MCP server acts as a proxy/deputy.

## Authorization and token checks

For HTTP authorization flows, inspect applicable evidence for:

- resource/audience binding and server validation of tokens intended for that MCP resource;
- no token passthrough to downstream services unless an explicit safe delegation design supports it;
- least privilege/scopes and short-lived/securely stored credentials where applicable;
- PKCE and authorization-code protection;
- exact redirect URI validation plus state correlation where the flow uses them;
- per-client/user consent and confused-deputy boundaries for proxy/delegating servers;
- authorization/protected-resource metadata origin validation and safe discovery/fetch behavior;
- fail-closed behavior for invalid/expired/wrong-audience tokens.

Do not apply HTTP OAuth requirements mechanically to `stdio`. For local/stdio servers, review environment/launch configuration, credential exposure in arguments/config, local process trust, filesystem permissions, and native-messaging/command boundaries instead.

## Tool/resource/prompt trust

Treat server-supplied names, descriptions, schemas, resources, prompt content, and tool results as potentially untrusted. Review:

- tool-description/metadata poisoning and whether model selection can be manipulated;
- schema/argument validation before side effects;
- resource URI/path traversal, SSRF, file/network scope, and unsafe rendering;
- prompt/resource content crossing trust boundaries into privileged instructions;
- server identity, version/provenance, and authorization scope changes after reconnect/update;
- state/task handles and any object authorization boundary when extensions introduce durable state.

## Evidence discipline

Bind protocol findings to the exact MCP/spec/security guidance version or source date used. A generic "MCP is insecure" claim is invalid. Static configuration does not prove runtime enforcement; runtime exploitability remains `needs-verification` unless demonstrated safely or supported by supplied runtime evidence.
