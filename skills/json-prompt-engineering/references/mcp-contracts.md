# MCP Structured Contracts

## Separate the contracts

Do not treat MCP as merely another model-output schema. Keep these identities distinct:

- tool `inputSchema`;
- tool `outputSchema`;
- successful `structuredContent` or equivalent structured result;
- textual compatibility content when the protocol/version requires it;
- tool execution errors;
- protocol errors;
- workflow/handoff schemas outside MCP.

## Protocol-version awareness

MCP evolves by protocol revision. Verify the active revision before relying on schema capabilities. For the 2026-07-28 specification snapshot used in the research corpus:

- tool input and output schemas follow JSON Schema usage rules and default to Draft 2020-12 when `$schema` is absent;
- input and output contracts are separate;
- clients and servers have distinct validation responsibilities;
- tool annotations must be treated as untrusted unless supplied by a trusted server.

Do not hard-code those details as guarantees for an unspecified future revision.

## Tool authority

Schema validity does not authorize a tool call. Independently enforce:

- authenticated principal/session;
- tool allowlist and operation policy;
- parameter validation;
- resource/file/network scope;
- side-effect class;
- rate/iteration bounds;
- confirmation/escalation policy for sensitive operations.

## Result validation

When `outputSchema` exists, validate successful structured tool results before passing them into downstream model context when the client/runtime supports validation. Keep tool errors outside the success schema unless the protocol contract explicitly models them inside it.
