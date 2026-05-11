# Agent Design Rubric

Use this rubric when designing or reviewing custom agents, agent prompts, agent tool contracts, and agentic structures.

## 1. Skill vs Agent Fit

Prefer a Skill when the requested behavior is a standardized competency, reusable checklist, artifact template, validator, or repeatable workflow that ChatGPT should apply on demand.

Prefer an Agent when the requested behavior needs one or more of these properties:

- mission-oriented operation with a named role;
- autonomous or semi-autonomous multi-step execution;
- coordination across other agents, Skills, humans, or tools;
- persistent task state within a session or repository workflow;
- routing, review, governance, or controlled execution responsibility.

Use a mixed system when a lightweight agent coordinates one or more specialist Skills. Keep the Skill as the capability owner and the Agent as the operator or orchestrator.

## 2. Role Quality Rubric

Score each dimension from 0 to 3.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Mission | vague | broad intent | clear objective | clear objective plus success criteria |
| Authority | absent | implied | stated | stated with decision rights and prohibitions |
| Responsibilities | generic | partial list | concrete list | concrete list with sequencing |
| Non-responsibilities | absent | generic warnings | concrete exclusions | exclusions tied to escalation rules |
| Inputs | unknown | examples only | required inputs | required inputs plus conservative defaults |
| Outputs | unspecified | prose only | structured output | structured output plus quality bar |
| Tools | tool list absent | broad tools | minimal required tools | minimal tools plus usage rules and fallbacks |
| Handoffs | absent | informal | defined targets | payload, trigger, and recipient contract defined |
| Validation | absent | checklist only | planned scenarios | scenarios with expected behavior and acceptance criteria |

Interpretation:

- 0-9: reject or redesign.
- 10-17: usable only for low-risk manual work.
- 18-23: acceptable with targeted improvements.
- 24-27: ready for controlled use.

## 3. Prompt Quality Requirements

A strong agent prompt includes:

1. Identity and mission: one direct statement of role and purpose.
2. Trigger context: when the agent should operate.
3. Responsibilities: specific actions the agent owns.
4. Non-responsibilities: explicit tasks the agent must not perform.
5. Tool contract: which tools it may use and why.
6. Workflow: ordered steps or decision tree.
7. Output contract: exact structure and level of detail.
8. Stop conditions: when to pause, escalate, or refuse.
9. Examples: only when examples reduce ambiguity.
10. Validation: expected behavior under normal and boundary cases.

Avoid:

- persona-heavy prose without operational rules;
- broad autonomy such as "do everything necessary";
- duplicated instructions copied from specialist Skills;
- hidden chain-of-thought requirements;
- tool lists that exceed the mission;
- claims that a tool exists when the runtime may not provide it.

## 4. Tool Contract Rubric

Classify each tool as one of:

- Required: the agent cannot fulfill its mission without it.
- Optional: improves quality but has a fallback.
- Forbidden: outside the role or too risky.
- Conditional: allowed only after a gate or user approval.

Least-authority defaults:

| Agent type | Default tools | Escalation before adding |
|---|---|---|
| Router | none or read-only context | any write, terminal, or execution tool |
| Governance reviewer | read-only repository/search | code edits, policy mutation, deployment |
| Prompt/agent designer | read-only plus file creation when requested | repository-wide edits or execution |
| Planner/context architect | search and read | direct code edits |
| Controlled executor | scoped edit and test tools | deployment, secrets, production operations |

## 5. Design Verdicts

Use these verdicts in reports:

- Approve: clear role, minimal tools, explicit boundaries, validation plan complete.
- Approve with changes: usable, but needs bounded fixes before routine use.
- Reject: unsafe authority, vague mission, missing stop conditions, excessive tools, or invalid routing.
- Blocked: critical runtime, repository, governance, or ownership input is missing.

## 6. Common Agent Archetypes

### Router Agent

Owns classification and dispatch. It should not solve specialist tasks. It should emit a compact routing decision, selected target, confidence, reason, and handoff payload.

### Governance Agent

Owns safety review, policy conformance, auditability, and escalation. It should prefer fail-closed recommendations for ambiguous high-impact actions.

### Review Agent

Owns inspection and findings. It should not apply changes unless explicitly designed as a repair agent with write authority.

### Controlled Execution Agent

Owns bounded execution steps. It must have preconditions, allowed paths, blocked paths, validation commands, rollback notes, and stop conditions.

### Prompt/Agent Designer

Owns converting requirements into agent instructions, not executing the final work the future agent will perform.
