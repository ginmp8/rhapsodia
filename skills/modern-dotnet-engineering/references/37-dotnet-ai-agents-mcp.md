# .NET AI, Agents, and MCP

## Activation boundary

Load this reference only when the .NET task materially involves model APIs, embeddings/RAG, agents, tool execution, or MCP. Ordinary APIs, workers, data access, and business logic should not acquire AI abstractions by default.

Because AI/provider/framework behavior changes quickly, verify current official package/framework documentation before making version-specific production claims.

## Microsoft.Extensions.AI

`Microsoft.Extensions.AI` provides common .NET abstractions such as `IChatClient` and `IEmbeddingGenerator`, plus middleware/decorator patterns around model clients.

Use these abstractions when provider portability, test substitution, telemetry/middleware, or shared cross-cutting behavior is a real requirement. Do not wrap a single provider behind another interface merely to add an interface.

## MCP decision rule

Use MCP when interoperable exposure of tools/resources/prompts across clients/agents is a concrete requirement. Do not introduce an MCP server merely to call internal methods that are already cleanly available in-process or through an existing API.

Model MCP tools/resources/prompts as security-sensitive external interfaces:

- explicit input/output schemas and bounded payloads;
- authentication plus operation/resource/tenant authorization;
- least-privilege tool authority;
- idempotency/confirmation for retryable or destructive actions;
- validation of model-supplied tool arguments as untrusted input;
- auditability without logging secrets/unnecessary prompt/context data;
- timeouts, cancellation, retry semantics, and rate/resource limits.

## Agent boundary

Use an agent/model for tasks where model judgment, planning, or tool selection adds value. Keep deterministic invariants, money/auth decisions, schema validation, and security controls in executable code/policy whenever they can be expressed deterministically.

Prompt instructions are guidance to the model, not an authorization boundary.

## Threat model

Review for:

- prompt injection and poisoned retrieved/tool/resource content;
- confused-deputy access to a different tenant/resource;
- excessive tool/API permissions;
- destructive action without confirmation/policy;
- secret/source/PII leakage to prompts, model providers, traces, or logs;
- model/provider/config changes that alter behavior while application code is unchanged.

## Reproducible evaluation

When comparing agent behavior, capture model/provider/configuration, prompt/system instructions, tool schemas, relevant retrieval/source snapshot, evaluator/scenario identity, and sampling parameters when exposed. Do not conflate model-quality metrics with application correctness/security.

## Validation gates

- schema/invalid-input tests for every executable tool/action boundary;
- negative authorization and cross-tenant/resource-ID tests;
- adversarial prompt/tool-injection and confused-deputy scenarios;
- idempotency/confirmation tests for destructive/retryable actions;
- data-handling review for prompts, logs, traces, and provider boundaries;
- human approval or equivalent strong policy gate for irreversible, credential, or production actions when consequences justify it.

Fresh source: https://learn.microsoft.com/dotnet/ai/microsoft-extensions-ai
