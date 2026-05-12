---
name: agent-design
description: use when asked to create, review, improve, validate, or structure custom agents, agent prompts, agent routing, agent governance, agent boundaries, agent tool contracts, handoffs, or repository agentic structures. especially useful for github copilot/vs code agents, routers, governance agents, review agents, controlled execution agents, and skill-agent coordination. do not use for creating chatgpt skills from scratch; use skill-creator for skill packages.
---

# Agent Design

## Purpose

Design, review, and validate custom agents that complement reusable Skills. Treat a Skill as a standardized capability and an Agent as an operator with a mission, authority boundary, state/context handling, and possible multi-step execution.

This skill does not depend on MCP or any external tool being available. If a user mentions MCP-backed agents as inspiration, translate the idea into portable agent instructions, explicit tool contracts, and safe handoffs.

## Core Rules

- Distinguish capability from operator: prefer a Skill for repeatable competency; prefer an Agent for mission-oriented coordination, stateful work, delegated execution, or multi-step operation.
- Do not use this skill to create or package ChatGPT Skills. Route Skill creation, repair, hardening, benchmarking, and improvement to the appropriate skill-package workflow.
- Do not design excessively autonomous agents without authority limits, stop conditions, escalation paths, and audit expectations.
- Do not mix agent design with executing the final technical task. Design the agent, its contract, and its validation plan; execution belongs to the selected agent, skill, or repository workflow.
- Keep routers lightweight. A router should classify, dispatch, and pass compact context; it must not copy the full instructions of each specialist.
- Never assume external tools, MCP servers, repository access, or write permissions. Model required tools as declared capabilities and mark unavailable tools as assumptions or integration requirements.

## Mode Selection

Use the smallest mode that satisfies the request. Combine modes only when the user asks for an end-to-end design package.

| User intent | Mode | Primary output |
|---|---|---|
| Understand a proposed agent | `agent-intake` | objective, inputs, outputs, tools, risks, assumptions |
| Define an agent role | `agent-role-design` | mission, authority, responsibilities, non-responsibilities |
| Write an agent prompt | `agent-prompt-design` | complete agent instructions or `.agent.md` content |
| Coordinate agents and Skills | `agent-routing-design` | routing matrix, handoff payloads, fallback rules |
| Review safety and controls | `agent-governance-review` | governance findings, stop conditions, auditability review |
| Review repository structure | `repo-agent-structure-review` | structure report for agents, prompts, instructions, Skills |
| Define validation evidence | `agent-validation-plan` | scenarios, expected behavior, acceptance criteria |
| Summarize a design package | `agent-design-report` | proposal, trade-offs, risks, next steps |

## Required Intake

Resolve or explicitly assume these before finalizing an agent design:

1. Agent objective and intended user.
2. Operating surface: chat mode, VS Code/GitHub Copilot `.agent.md`, repository workflow, governance workflow, review workflow, or generic agent instructions.
3. Inputs, context sources, expected outputs, and output format.
4. Tool contract: read-only, write-capable, terminal-capable, web-capable, repository-capable, or no tools.
5. Authority boundary: what the agent may decide, change, execute, approve, reject, or escalate.
6. Stop conditions and human-in-the-loop triggers.
7. Handoffs to Skills, agents, humans, or repository processes.
8. Validation scenarios and acceptance criteria.

If these are incomplete, proceed with conservative assumptions and list them. Ask a follow-up only when the missing item changes the safety boundary or makes the requested output impossible.

## Progressive Loading

Load only the resource needed for the active mode:

- `references/agent-design-rubric.md`: use for role quality, prompt quality, tool contract, autonomy, and validation scoring.
- `references/agent-governance-patterns.md`: use for authority limits, safety boundaries, audit trails, stop conditions, escalation, and controlled execution.
- `references/routing-and-handoff-patterns.md`: use for router agents, Skill-vs-Agent dispatch, handoff payloads, nomia/Mago/Magia integration, and lightweight orchestration.
- `references/agent-validation-scenarios.md`: use when defining planned tests, expected behavior, adversarial cases, regression checks, or acceptance criteria.
- `assets/templates/agent-spec.md.template`: copy and fill when the user wants a reusable agent specification.
- `assets/templates/agent-review-report.md.template`: copy and fill when the user wants a structured governance or quality review.

## Workflow

1. Select the mode and state the assumed operating surface.
2. Run intake: objective, inputs, outputs, tools, authority, handoffs, stop conditions, risks.
3. Decide whether the request is a Skill problem, Agent problem, or mixed Skill-Agent system.
4. Design the role, responsibilities, non-responsibilities, and tool contract.
5. Draft the agent prompt or `.agent.md` content when requested.
6. Add routing and handoff rules only when multiple agents or Skills are involved.
7. Run governance review against stop conditions, auditability, escalation, least authority, and controlled execution.
8. Define validation scenarios with expected behavior and acceptance criteria.
9. Deliver a design report with trade-offs, risks, limitations, and next steps.

## VS Code and GitHub Copilot Agent Defaults

When drafting a VS Code/GitHub Copilot custom agent, prefer this shape unless the user supplies a stricter convention:

```markdown
---
description: brief action-oriented purpose
name: Human Readable Agent Name
tools: [read_file, search, semantic_search]
---

# Agent Name

## Role
...

## Responsibilities
...

## Boundaries
...

## Workflow
...

## Output Contract
...

## Stop Conditions
...
```

Use lowercase-with-hyphens filenames such as `.github/agents/governance-reviewer.agent.md`. Select only the minimal tools needed for the mission. For review, planning, governance, or routing agents, default to read-only tools. Add edit, terminal, or execution tools only when the role truly requires controlled execution.

## Output Contracts

### Agent design

Return:

1. agent name and operating surface;
2. objective and target users;
3. inputs, outputs, and tool contract;
4. authority boundary and stop conditions;
5. complete prompt or `.agent.md` content when requested;
6. handoffs and routing rules when relevant;
7. validation scenarios and acceptance criteria;
8. risks, trade-offs, and limitations.

### Agent review

Return:

1. verdict: approve, approve with changes, or reject;
2. critical findings and evidence;
3. boundary and authority assessment;
4. tool contract assessment;
5. safety, auditability, and escalation assessment;
6. concrete fixes;
7. validation plan.

### Repository structure review

Return:

1. detected structure and intended platform;
2. missing or misplaced files;
3. naming and frontmatter findings;
4. duplication between agents, prompts, instructions, and Skills;
5. recommended structure;
6. migration or cleanup plan.

## Stop Conditions

Stop or return a blocker when:

- the user asks this skill to create or package a ChatGPT Skill instead of designing agents;
- requested autonomy lacks an authority boundary for write, execution, deployment, approval, financial, security, identity, or production-impacting actions;
- a router would need to execute specialist responsibilities instead of dispatching;
- the requested agent depends on unavailable tools and no tool contract assumption is acceptable;
- the request asks for hidden, unauditable, self-modifying, policy-bypassing, or uncontrolled execution behavior;
- validation evidence is requested as measured but no execution results are available.

## Final Checklist

Before claiming the design is ready:

- Skill vs Agent fit is explicit.
- The agent has a clear mission, authority, non-responsibilities, and output contract.
- The tool contract follows least authority.
- Stop conditions and escalation paths exist.
- Handoffs are compact and do not duplicate specialist instructions.
- Governance and audit expectations are defined for risky actions.
- Validation scenarios include normal, ambiguous, boundary, failure, and adversarial cases.
- Limitations and assumptions are stated without claiming unavailable tools or measured results.
