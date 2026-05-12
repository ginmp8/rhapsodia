# Routing and Handoff Patterns

Use this reference when designing agent routers, Skill-Agent coordination, governance handoffs, and repository agentic structures.

## Routing Principles

- Keep routers thin: classify intent, select target, produce a compact handoff payload, and stop.
- Do not copy specialist instructions into the router. Store expertise in specialist agents or Skills.
- Use explicit routing criteria rather than broad persona descriptions.
- Include fallback behavior for low confidence, missing context, conflicting targets, or unavailable tools.
- Make Skill-vs-Agent selection explicit.

## Skill vs Agent Routing

Route to a Skill when:

- the request is a repeatable competency or packaged workflow;
- the output depends on fixed templates, rubrics, validators, or references;
- the goal is consistency rather than autonomous operation;
- the user asks to create, repair, harden, benchmark, package, or improve a Skill package.

Route to an Agent when:

- the request needs a mission-oriented operator;
- there is multi-step coordination, state, or delegation;
- the agent must choose between tools, paths, or handoffs;
- governance, review, routing, or controlled execution is the primary role.

Route to a human when:

- authority is unclear;
- risk is high-impact;
- required approval is missing;
- the router cannot classify confidently;
- the requested action would violate stop conditions.

## Routing Matrix Template

| Intent signal | Target | Confidence rule | Required context | Handoff payload | Fallback |
|---|---|---|---|---|---|
| create or package ChatGPT Skill | `skill-creator` | high when artifact is `SKILL.md`/`skill.zip` | objective, inputs, outputs | skill request summary | ask for missing inputs |
| design custom agent | `agent-design` | high when artifact is agent prompt or `.agent.md` | role, tools, boundaries | agent design intake | run conservative intake |
| plan repository architecture | `mago` or repository architect agent | high when planning artifacts are requested | spec, repo, constraints | planning scope | request resolved spec |
| execute bounded repo work | `magia` or executor agent | high when implementation is requested | plan, allowed paths, tests | execution package | stop if authority missing |
| delivery governance/status | `nomia` or governance agent | high when roadmap/status/owner data is requested | demand, owner, due date | governance record | stop if ownership missing |

Adapt target names to the user's actual ecosystem.

## Handoff Payload Pattern

A good handoff is compact and complete:

```markdown
## Handoff
- source: router or previous agent
- target: selected agent, Skill, or human
- objective: what the target should accomplish
- context: only the relevant facts and constraints
- inputs: files, links, artifacts, or text to inspect
- authority: what the target may and may not do
- expected output: exact deliverable
- stop conditions: when to pause or escalate
- validation: checks or acceptance criteria
```

Avoid sending full transcripts, hidden reasoning, irrelevant source material, secrets, or copied specialist prompts.

## Router Agent Prompt Pattern

```markdown
# Router Agent

## Role
You classify user requests and route them to the correct agent, Skill, or human. You do not execute specialist work.

## Routing Workflow
1. Identify the user's intended artifact and outcome.
2. Classify the request as Skill, Agent, repository planning, repository execution, governance, review, or human escalation.
3. Select one target and state confidence.
4. Build a compact handoff payload.
5. Stop after routing unless the user asked for a routing matrix.

## Output Contract
- route:
- confidence: high | medium | low
- reason:
- required context:
- handoff payload:
- fallback or escalation:

## Stop Conditions
Stop when confidence is low, when authority is unclear, or when the request asks the router to perform specialist execution.
```

## nomia/Mago/Magia Integration

Use these boundaries when designing agents for the user's ecosystem:

- nomia: product/delivery governance, demand intake, owners, stakeholders, roadmap bookkeeping, portfolio, release notes, status, replanning, and governance decision logs.
- Mago: tech-lead planning artifacts, PRD refinement, architecture decisions, technical design, implementation plans, validation plans, migrations, observability, and security considerations.
- Magia: bounded implementation, debugging, tests, validation, hardening, documentation, execution notes, runbooks, and execution-grounded decisions.

Recommended agent structure:

1. Governance router: classifies whether a request belongs to nomia, Mago, Magia, skill optimization, or human escalation.
2. nomia agent: manages delivery metadata and stakeholder-facing governance artifacts only.
3. Mago agent: plans and refines technical work, but does not implement.
4. Magia agent: executes bounded work from current code and selected planning artifacts.
5. Governance reviewer agent: reviews authority, auditability, stop conditions, and handoffs across the system.
6. Skill optimizer agents or Skills: use skill-consistency-repair, skill-harness, skill-hardening, skill-improver, and skill-benchmark for Skill-package lifecycle work.

Do not let one mega-agent own all layers. Use routing plus explicit handoff contracts.

## Repository Structure Pattern

For GitHub Copilot/VS Code-oriented repositories, review or propose structures like:

```text
.github/
  copilot-instructions.md
  agents/
    router.agent.md
    governance-reviewer.agent.md
    controlled-executor.agent.md
  prompts/
    review-agent.prompt.md
  instructions/
    dotnet.instructions.md
  skills/
    skill-name/
      SKILL.md
```

Review for:

- lowercase-with-hyphens filenames;
- `.agent.md`, `.prompt.md`, `.instructions.md`, and `SKILL.md` extensions;
- separation between foundation instructions, specialist agents, reusable prompts, file-specific instructions, and Skills;
- no circular handoffs;
- no duplicated specialist content in routers;
- no write-capable tools in review-only agents;
- no missing description/frontmatter in agent and prompt files.
