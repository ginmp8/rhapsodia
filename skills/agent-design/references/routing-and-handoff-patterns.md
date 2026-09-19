# Routing and Handoff Patterns

Use this reference for router agents, supervisor/worker systems, Skill-Agent coordination, governance handoffs, and repository agentic structures. The portable routing core uses `agent-design-contract/v1` and `handoff/v1`.

## Routing Principles

- Keep routers thin: classify, select, emit a compact handoff, and stop.
- Route by owned artifact/outcome and authority fit, not persona similarity.
- Do not copy specialist prompts or capability instructions into the router.
- Prefer least authority when multiple targets can satisfy the request.
- Make low-confidence and unavailable-target behavior explicit.
- Keep the core catalog-independent: specialist names are configuration, not routing logic.

## Routing Decision Order

When more than one target appears eligible, apply this order:

1. **Exact output ownership**: which target owns the requested deliverable or decision?
2. **Authority fit**: which target can complete it without broader authority than necessary?
3. **Required context/capabilities**: which target has or can receive the required inputs and tools?
4. **Operating-surface compatibility**: which target is valid for the current host/repository/workflow?
5. **Explicit organization/user rule**: apply configured ownership when it does not conflict with higher-level constraints.
6. **Escalation**: if a material tie remains, do not route randomly; ask a bounded question or escalate to the owning human/supervisor.

### Confidence vocabulary

Use qualitative confidence only:

- `high`: one target uniquely satisfies ownership, authority, and required context.
- `medium`: one target is best supported but a non-safety-critical assumption or fallback is required.
- `low`: multiple material targets remain, ownership/authority is unresolved, or required context is missing.

`low` confidence must not dispatch a high-impact action. Do not invent numeric probabilities.

## Skill vs Agent Routing

Route to a Skill workflow when the request is primarily a reusable competency, fixed validator/template, or Skill-package lifecycle task.

Route to an Agent when the request needs mission ownership, state, routing, supervision, governance, or controlled multi-step execution.

Route to a human/supervisor when authority, ownership, approval, or a material routing tie remains unresolved.

For mixed systems, the Agent owns coordination and the Skill owns its reusable capability. Do not duplicate the Skill inside the Agent prompt.

## Handoff Payload Pattern

Use `handoff/v1` when a structured handoff is useful:

```markdown
## Handoff
- contract: handoff/v1
- source: router or previous actor
- target: selected agent, Skill, or human
- objective: single owned outcome
- context: only relevant facts and constraints
- inputs: files, links, artifacts, or identifiers
- authority: recipient may / must-not / escalate summary
- expected output: exact deliverable
- stop conditions: blockers or escalation triggers
- validation: acceptance checks
- route trace: prior route identifiers/roles when cycle detection is needed
```

Avoid full transcripts, hidden reasoning, secrets, unrelated source material, or copied specialist instructions.

## Cycle and Re-entry Safety

A routing topology must have an observable termination rule.

- Do not allow unbounded A -> B -> A loops.
- Workers should not delegate to other workers unless the topology explicitly grants that responsibility.
- Re-entry to a prior target requires a material state change: new evidence, a changed artifact, an explicit repair result, or a new authorization decision.
- A repeated handoff with materially identical state is a stop/escalation condition.
- If intentional loops exist, define a finite hop/iteration budget or an equivalent terminating predicate.
- If no loop rule is provided, default to **no cyclic re-entry**.
- When runtime state exists, track route/handoff identity and visited roles. When it does not, include a compact route trace in `handoff/v1`.

## Router Agent Pattern

```markdown
# Router Agent

## Role
Classify requests and route them to the configured owner. Do not execute specialist work.

## Routing Workflow
1. Identify the requested artifact/outcome.
2. Determine Skill, Agent, human, or configured specialist ownership.
3. Apply the routing decision order.
4. Emit route, confidence, reason, and `handoff/v1` payload.
5. Stop after handoff or escalation.

## Output Contract
- route:
- confidence: high | medium | low
- ownership reason:
- required context:
- handoff:
- fallback/escalation:

## Stop Conditions
Stop on low confidence, unresolved authority/ownership, unavailable required capability, repeated identical handoff, or a request to perform specialist execution.
```

## Optional Ecosystem Adapter: nomia / Mago / Magia

Use these names only when the user's configured ecosystem contains them; they are not portable core dependencies.

- **nomia**: product/delivery governance, intake, owners, stakeholders, roadmap/status, releases, and governance records.
- **Mago**: technical planning, PRD refinement, architecture/design, implementation and validation plans, migrations, observability, and security planning.
- **Magia**: bounded implementation, debugging, tests, validation, hardening, documentation, runbooks, and execution-grounded decisions.

A typical hub-and-spoke topology is:

1. lightweight router/supervisor owns classification and handoff;
2. nomia owns delivery-governance outputs;
3. Mago owns technical planning outputs;
4. Magia owns bounded implementation outputs;
5. a governance reviewer may independently review authority and auditability;
6. Skill-package lifecycle work routes to the configured Skill workflow/router rather than hard-coding the full Skill catalog here.

Do not let workers recursively delegate across layers unless the user explicitly designs that topology.

## Repository Structure Pattern

For GitHub Copilot/VS Code-oriented repositories, a common separation is:

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
- correct host-specific extensions/frontmatter;
- separation of foundation instructions, specialist agents, reusable prompts, file-specific instructions, and Skills;
- no unbounded circular handoffs;
- no duplicated specialist content in routers;
- no unjustified write-capable tools in review/router agents;
- explicit termination and handoff ownership.
