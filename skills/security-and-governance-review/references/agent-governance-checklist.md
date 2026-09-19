# Agent Governance Checklist

Use this checklist for `llm-agent-governance-review`.

## Authority-boundary matrix

For every meaningful capability, record the boundary explicitly:

| Action | Resource scope | Authorization source | Approval | Audit/receipt | Failure behavior | Rollback/containment |
|---|---|---|---|---|---|---|
| read/write/execute/delete/send/publish/schedule/deploy/approve/delegate | exact target | user/policy/config/system | none/explicit/human | required/not applicable | fail closed/fail open | concrete control |

Capability is not authorization. When authorization or target identity is ambiguous for a high-impact action, fail closed and classify the gap `governance-risk` or `needs-verification` based on the evidence available.

## Inspect

- What the agent may read, write, execute, delete, send, schedule, publish, deploy, approve, or delegate.
- Which actions require explicit user/human authorization.
- Which paths/resources are blocked or read-only.
- Network, terminal, email, calendar, repository, browser, connector, and subagent authority.
- Cross-agent trust boundaries and whether delegated authority can exceed the caller's authority.

## Policy enforcement

Look for explicit allowlists/denylists, scoped mutation, human approval for high-impact actions, rate/budget limits, retries/timeouts, fail-closed policy, rollback/containment, and separation of governance logic from business logic.

Do not infer a policy from tool availability, UI capability, or a broad system role. Missing policy evidence stays `needs-verification`.

## Audit and observability

Look for append-only or tamper-evident records of tool calls, approvals, denied actions, handoffs, policy decisions, and remediation actions. Evidence should distinguish command/tool output, reviewer judgment, assumptions, and planned scenarios.

## LLM-specific controls

Inspect prompt-injection boundaries, data exfiltration controls, context provenance, secret redaction, untrusted-content handling, stop conditions, and escalation for authority-escalating requests.

## Handoff and fallback

Record the owner of unresolved risk, escalation path, what happens when scanner/manifests/policy/current vulnerability evidence is unavailable, and whether the workflow avoids silent success. Critical missing authorization evidence must block positive assurance.
