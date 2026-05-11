# Agent Governance Checklist

Use this checklist for `llm-agent-governance-review`.

## Authority boundaries

Inspect whether the agent or skill states:

- What it may read, write, execute, delete, send, schedule, or publish.
- Which actions require explicit user authorization.
- Which paths and resources are blocked.
- Whether it can use network, terminal, email, calendar, repository, browser, or connector tools.
- Whether it can call other agents, delegate work, or hand off decisions.

## Policy enforcement

Look for:

- Explicit allowlists for tools, paths, commands, domains, and mutation scopes.
- Deny rules for secrets, credentials, `.git`, expected outputs, generated evidence, fixtures, and destructive commands.
- Fail-closed behavior on ambiguous permissions, uncertain target identity, or missing policy context.
- Human-in-the-loop approval for high-impact operations.
- Rate limits, budget limits, retries, timeouts, and rollback rules.
- Separation of governance logic from business logic.

## Audit and observability

Look for:

- Append-only audit trail guidance for tool calls, policy decisions, denied actions, approvals, handoffs, and remediation actions.
- Evidence records that distinguish command output, reviewer judgment, assumptions, and planned scenarios.
- Report sections for validation commands, blocked paths, residual risks, and limitations.

## LLM security

Look for:

- Prompt injection handling when untrusted content is summarized, transformed, or used as instructions.
- Data exfiltration controls for secrets and sensitive internal content.
- Context boundary rules that separate user content, system/developer instructions, target files, and tool outputs.
- Output filtering or redaction for sensitive data.
- Stop conditions for malicious, destructive, or authority-escalating requests.

## Handoff and fallback

Look for:

- Clear owner for unresolved risks.
- When to escalate to human review, security, legal, compliance, or product owner.
- What to do when scanner evidence, manifests, policy, or current vulnerability data is unavailable.
- No silent success when evidence is missing.
