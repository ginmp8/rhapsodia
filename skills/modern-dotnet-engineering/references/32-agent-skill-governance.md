# Agent and Skill Governance

## Use when

The task involves agents, skills, automated code changes, CI agents, AI-assisted workflows, or tool execution. For concrete .NET AI/MCP platform guidance also load `references/37-dotnet-ai-agents-mcp.md`.

## Rules

- Define authority boundaries: read-only, write, execute, deploy, credential, and destructive actions.
- Require explicit approval/strong policy gates for destructive, credential, production, financial, or irreversible actions.
- Prefer fail-closed behavior when permissions are ambiguous.
- Treat model output, prompt content, retrieved context, and tool/resource arguments as untrusted input.
- Do not expose secrets in prompts, logs, examples, generated diagnostics, or outputs.
- Keep audit trails for high-impact agent actions without logging unnecessary sensitive prompt/tool data.
- Validate generated artifacts and executable tool arguments before packaging/execution.
- Enforce authorization and tenant/resource ownership at the executable boundary; prompt instructions are not a security boundary.
- Freeze model/provider/config identity when comparing agent behavior reproducibly.

## Review dimensions

- tool authority and least privilege;
- file/resource mutation scope;
- schema/input validation;
- executable authorization and confused-deputy risk;
- prompt/tool/resource injection;
- script safety and dependency risk;
- sensitive data handling;
- model/provider/config drift;
- rollback, human approval, and validation gates.
