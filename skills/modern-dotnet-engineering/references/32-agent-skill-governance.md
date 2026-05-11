# Agent and Skill Governance

## Use when

The task involves agents, skills, scripts, validators, automated code changes, CI agents, tool permissions, or AI-assisted workflows.

## Rules

- Define authority boundaries: read-only, write, execute, deploy.
- Require human approval for destructive, credential, production, or financial actions.
- Prefer fail-closed behavior when permissions are ambiguous.
- Do not expose secrets in prompts, logs, examples, or outputs.
- Keep audit trails for high-impact agent actions.
- Validate generated artifacts before packaging or execution.

## Review dimensions

- tool authority;
- file mutation scope;
- script safety;
- dependency risk;
- prompt/skill instructions;
- sensitive data handling;
- rollback and validation gates.
