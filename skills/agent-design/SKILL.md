---
name: agent-design
description: use when asked to design, review, improve, validate, or structure custom agents, agent prompts, agent routing/orchestration, authority boundaries, tool contracts, handoffs, state/termination, governance, or repository agentic structures. especially useful for github copilot/vs code agents, routers, supervisors, review/governance agents, controlled executors, and skill-agent coordination. do not use to create/package skills or to execute the downstream technical task itself.
---

# Agent Design

## Purpose

Design, review, and validate custom agents as bounded operators around reusable capabilities. Treat a Skill as a standardized capability and an Agent as an operator with a mission, owned outcome, authority boundary, tool contract, state/termination behavior, and possible multi-step coordination.

The portable core does not require MCP or any single host. Translate host-specific ideas into explicit capabilities, contracts, and adapters.

## Activation Contract

Activate when the requested artifact or analysis is primarily one of:

- an agent role, prompt, `.agent.md`, or reusable agent specification;
- router/supervisor/worker topology or handoff design;
- agent authority, tool, stop, escalation, state, or termination contract;
- governance/review of an existing agent;
- repository organization for agents/prompts/instructions/Skills;
- validation scenarios for agent behavior.

Do **not** own the request when the primary outcome is:

- creating, repairing, hardening, benchmarking, or packaging a Skill package;
- implementing/debugging the downstream repository task rather than designing its future agent;
- merely writing a normal prompt with no agent role, authority, state, routing, or operating contract;
- executing a production/deployment/financial/identity/security action that belongs to another authorized workflow.

For mixed requests, design the Agent portion and hand the capability/execution portion to the configured owner. Do not duplicate another Skill or specialist's instructions inside the Agent.

## Core Rules

- Prefer a Skill for repeatable competency; prefer an Agent for mission ownership, state, coordination, governance, routing, or controlled execution.
- Design only the authority actually required by the mission. Missing high-impact authority is a blocker, not implicit permission.
- Separate design/review from downstream execution unless the requested artifact itself is a controlled-executor design.
- Keep routers thin: classify, select, emit `handoff/v1`, and stop.
- Never assume tools, MCP servers, repository access, network access, write permissions, or background execution.
- Stateful or multi-agent designs require finite termination and cycle/re-entry behavior.
- Planned scenarios are not measured behavioral validation.

## Mode Selection

Choose the smallest mode that owns the requested outcome. Combine modes only when the user requests an end-to-end design package.

| User intent | Mode | Primary output |
|---|---|---|
| Understand a proposed agent | `agent-intake` | objective, ownership, inputs, outputs, capabilities, risks, assumptions |
| Define an agent role | `agent-role-design` | mission, authority, responsibilities, state/termination |
| Write an agent prompt | `agent-prompt-design` | complete instructions or `.agent.md` |
| Coordinate agents and Skills | `agent-routing-design` | topology, routing rules, `handoff/v1`, fallback, cycle safety |
| Review safety/controls | `agent-governance-review` | critical gates, findings, stop/escalation, auditability |
| Review repository structure | `repo-agent-structure-review` | ownership/placement/duplication/topology report |
| Define validation evidence | `agent-validation-plan` | frozen scenarios, expected behavior, evidence/acceptance rules |
| Summarize a design package | `agent-design-report` | contract, trade-offs, evidence, residual risks |

## Decision Rules

Apply decisions in this order:

1. Identify the requested artifact/outcome and its owner.
2. Classify the problem as Skill, Agent, mixed system, repository execution, or human/governance decision.
3. Select the narrowest mode and agent archetype that can own the outcome.
4. Minimize authority and capabilities before adding convenience tools.
5. Resolve routing conflicts using exact output ownership, authority fit, context/capability availability, operating-surface compatibility, then explicit configured routing rules.
6. If a material tie or high-impact authority ambiguity remains, ask one bounded question or escalate; do not route randomly.
7. Apply critical governance gates before advisory scoring.

Detailed routing tie-breakers and confidence semantics live in `references/routing-and-handoff-patterns.md`.

## Required Intake

Resolve or conservatively declare:

1. agent objective, owned outcome, and intended caller/user;
2. operating surface;
3. required inputs/context and expected outputs;
4. capability/tool contract (`required | optional | conditional | forbidden`);
5. authority boundary (`may decide | may recommend | may execute | must not execute | must escalate`);
6. state and termination behavior when stateful/multi-step;
7. stop conditions and human/supervisor triggers;
8. handoffs/routing topology when multiple actors exist;
9. validation scenarios and evidence status.

Ask a follow-up only when missing information changes a safety/authority boundary or makes the requested artifact impossible. Otherwise use conservative assumptions and label them.

## Progressive Loading

Load only what the active mode needs:

- `references/agent-contracts.md`: canonical `agent-design-contract/v1`, authority, tool, state, completion, evidence, and `handoff/v1` semantics.
- `references/agent-design-rubric.md`: `agent-design-rubric/v2`, critical gates, severity, advisory scoring, archetypes.
- `references/agent-governance-patterns.md`: authority limits, audit trails, high-impact actions, controlled execution, failure/rollback expectations.
- `references/routing-and-handoff-patterns.md`: deterministic routing order, confidence vocabulary, handoff payloads, cycle/re-entry safety, optional ecosystem adapters.
- `references/agent-validation-scenarios.md`: frozen scenario design, evidence labels, baseline/candidate comparison, structural validation.
- `evals/agent-design-scenarios.json`: frozen planned scenario suite for this skill; do not call it executed evidence until a harness actually runs it.
- `assets/templates/agent-spec.md.template`: reusable durable agent specification.
- `assets/templates/agent-review-report.md.template`: structured review/governance report.

## Workflow

1. Select mode and operating surface.
2. Run intake and state assumptions/evidence strength.
3. Determine Skill-vs-Agent ownership and the exact agent-owned outcome.
4. Define mission, responsibilities, non-responsibilities, authority, and capabilities.
5. For stateful work, define state transitions, terminal states, re-entry/retry rules, and failure behavior.
6. For multi-agent work, define topology, deterministic routing, `handoff/v1`, fallback, and cycle safety.
7. Draft the prompt/spec/`.agent.md` when requested.
8. Run governance review using critical gates from `agent-design-rubric/v2` before any advisory score.
9. Define validation scenarios and label them `planned | executed | supplied`.
10. When a file artifact is available, run the structural validator; keep semantic/runtime claims separate.
11. Deliver the requested artifact plus only the evidence, risks, and limitations needed to interpret it.

## Multi-Agent State and Termination

For routers, supervisors, delegated execution, repair loops, or any re-entrant workflow:

- declare who owns orchestration state;
- define terminal outcomes (`completed`, `blocked/escalated`, or equivalent);
- forbid repeated materially identical handoffs;
- require a material state change for re-entry;
- define a finite loop/hop/repair bound or equivalent terminating predicate;
- if no loop policy is specified, default to **no cyclic re-entry**;
- prevent workers from recursively delegating unless that responsibility is explicit.

Do not add multi-agent complexity when a single bounded agent or Skill is sufficient.

## VS Code and GitHub Copilot Defaults

When drafting a VS Code/GitHub Copilot custom agent, prefer this host adapter unless the repository defines another convention:

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

Use lowercase-with-hyphens filenames such as `.github/agents/governance-reviewer.agent.md`. Start review, planning, governance, and routing roles read-only. Add mutation/terminal/execution capabilities only when the authority contract requires them.

## Reproducibility and Evidence

Use the evidence vocabulary from `agent-design-contract/v1`:

- `measured`: executed validator/scenario/runtime evidence;
- `observed`: directly inspected artifact/source;
- `supplied`: externally provided evidence;
- `inferred`: reasoned conclusion;
- `planned`: not executed;
- `blocked`: unavailable.

Keep structural, behavioral, and runtime evidence separate. A valid Markdown shape does not prove the agent will behave correctly; a planned scenario does not prove behavior was tested.

For generated files, run when possible:

```text
<PYTHON> scripts/validate_agent_artifact.py <ARTIFACT> --kind auto --profile <PROFILE> --json <RECEIPT>
```

For this skill package itself:

```text
<PYTHON> scripts/validate_agent_design_package.py --target <SKILL_ROOT> --json <RECEIPT>
```

The validators emit machine-readable diagnostics and intentionally do not claim semantic correctness.

## Output Contracts

### Agent design

Return, as applicable:

1. name, operating surface, contract identity, and owned outcome;
2. objective/users, inputs/context, and outputs;
3. authority and tool/capability contract;
4. state/termination and stop/escalation behavior;
5. complete prompt or `.agent.md` when requested;
6. routing/handoffs and cycle rules when relevant;
7. validation scenarios and evidence status;
8. material risks/trade-offs/assumptions.

### Agent review

Return:

1. verdict from critical-gate rules;
2. critical gates with evidence labels;
3. findings using stable severity and criterion/evidence/fix mapping;
4. authority/tool/state/routing assessment as applicable;
5. concrete required fixes;
6. validation plan and explicit not-measured items.

### Repository structure review

Return:

1. detected structure/host;
2. ownership and placement findings;
3. naming/frontmatter/authority/tool issues;
4. duplication among agents/prompts/instructions/Skills;
5. routing/cycle/termination issues;
6. bounded migration/cleanup plan.

## Stop Conditions

Stop or return a blocker when:

- the request belongs to Skill-package creation/improvement rather than agent design;
- high-impact autonomy lacks explicit authority;
- required ownership or operating surface is unresolved and changes safety/correctness;
- a router would need to execute specialist responsibilities;
- a stateful topology has no safe termination/re-entry contract;
- a required capability is unavailable and no valid fallback/handoff exists;
- the request requires hidden, unaudited, self-modifying, policy-bypassing, or uncontrolled behavior;
- measured validation is requested but no executed evidence exists.

## Final Validation and Freeze

Before calling a design ready:

- Skill-vs-Agent fit and owned outcome are explicit.
- Critical gates pass or the result is correctly `blocked/reject/approve with changes`.
- Authority follows least privilege.
- Stateful/multi-agent designs have termination and cycle safety.
- Handoffs are compact and versioned when structure matters.
- Validation scenarios cover activation/non-activation, ambiguity, core, edge/failure, regression, and adversarial behavior as relevant.
- Evidence claims match what was actually executed/observed/supplied.
- Structural validators pass when applicable.

After the final validation pass, treat the candidate as frozen. Any material edit invalidates the affected evidence and requires revalidation.
