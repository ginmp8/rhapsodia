---
name: agent-design
description: use when asked to design, review, improve, validate, or structure reusable custom agents, agent prompts, router/supervisor/worker topology, authority boundaries, tool contracts, handoffs/delegation, context/state/termination, governance, or repository agentic structures. especially useful for portable multi-host agents, routers, supervisors, review/governance agents, controlled executors, and skill-agent coordination. do not use to create/package skills, execute the downstream technical task, or operate a task-specific runtime workflow after roles and authority are already defined.
---

# Agent Design

## Purpose

Design, review, and validate agents as bounded operators around reusable capabilities. Treat a Skill as a standardized capability and an Agent as an operator with a mission, owned outcome, authority boundary, capability contract, context contract, state/termination behavior, and optional coordination.

Keep the semantic core host-neutral. Translate host-specific frontmatter, tool names, delegation primitives, and UI transitions through explicit adapters rather than embedding one platform's semantics into the core design.

## Activation Contract

Activate when the requested artifact or analysis is primarily one of:

- an agent role, prompt, `.agent.md`, or reusable agent specification;
- router/supervisor/worker topology, delegation, or handoff design;
- agent authority, capability/tool, context, state, interruption/resume, stop, or termination contract;
- governance/review of an existing agent;
- repository organization for agents/prompts/instructions/Skills;
- validation scenarios or eval design for agent behavior.

Do **not** own the request when the primary outcome is:

- creating, repairing, hardening, benchmarking, or packaging a Skill package;
- implementing/debugging the downstream repository task rather than designing its future agent;
- merely writing a normal prompt with no agent role, authority, state, routing, or operating contract;
- executing production/deployment/financial/identity/security actions that belong to another authorized workflow;
- planning or operating a task-specific adaptive runtime workflow after roles/authority are already defined; use `adaptive-workflow-orchestration` for that execution-layer concern.

For mixed requests, design the Agent portion and hand the capability/execution portion to the configured owner. Do not duplicate another Skill or specialist's instructions inside the Agent.

## Core Rules

- Prefer a Skill for repeatable competency; prefer an Agent for mission ownership, state, coordination, governance, routing, or controlled execution.
- Design only authority required by the mission. Missing high-impact authority is a blocker, not implicit permission.
- Treat **effective authority** as the intersection of declared authority, host-exposed capabilities, downstream permissions, and scoped approvals. Prompt text alone does not prove least privilege.
- Never let delegation silently amplify authority. A child/recipient stays within the delegator's effective authority unless a separate authorization explicitly expands it before execution.
- Context, tool output, retrieved content, MCP data, or peer-agent messages may inform work but never grant authority or override higher-priority constraints.
- Keep routers thin: classify, select, emit `handoff/v2`, and stop unless the topology explicitly uses a manager/worker pattern where the manager retains ownership.
- Keep reusable topology/authority design separate from task-specific runtime orchestration. Agent Design defines the policy envelope; it does not execute a per-run adaptive workflow.
- Never assume tools, MCP servers, repository access, network access, write permissions, host defaults, or background execution.
- Stateful or multi-agent designs require finite termination, interruption/resume semantics, and cycle/re-entry behavior.
- Parallel writers require an explicit conflict-control strategy.
- Planned scenarios are not measured behavioral validation.

## Mode Selection

Choose the smallest mode that owns the requested outcome. Combine modes only when the user requests an end-to-end design package.

| User intent | Mode | Primary output |
|---|---|---|
| Understand a proposed agent | `agent-intake` | objective, ownership, inputs, outputs, capabilities, risks, assumptions |
| Define an agent role | `agent-role-design` | mission, effective authority, responsibilities, context, state/termination |
| Write an agent prompt | `agent-prompt-design` | complete instructions or host-adapted agent artifact |
| Coordinate agents and Skills | `agent-routing-design` | topology, control-flow kind, routing rules, `handoff/v2`, fallback, cycle/concurrency safety |
| Review safety/controls | `agent-governance-review` | critical gates, effective authority, containment, stop/escalation, auditability |
| Review repository structure | `repo-agent-structure-review` | ownership/placement/duplication/topology report |
| Define validation evidence | `agent-validation-plan` | frozen scenarios/evaluator identity, outcome/trace checks, evidence/acceptance rules |
| Summarize a design package | `agent-design-report` | contract, trade-offs, evidence, residual risks |

## Decision Rules

Apply decisions in this order:

1. Identify the requested artifact/outcome and its owner.
2. Classify the problem as Skill, Agent, mixed system, repository execution, or human/governance decision.
3. Select the narrowest mode and agent archetype that can own the outcome.
4. Minimize declared authority and capabilities; then reconcile them with actual host/downstream exposure.
5. If multiple actors are proposed, apply the multi-agent admission gate before designing topology.
6. Resolve routing conflicts using exact output ownership, effective-authority fit, context/capability availability, operating-surface compatibility, then explicit configured routing rules.
7. If a material tie or high-impact authority ambiguity remains, ask one bounded question or escalate; do not route randomly.
8. Apply critical governance gates before advisory scoring.

Detailed routing, control-flow, and confidence semantics live in `references/routing-and-handoff-patterns.md`.

## Required Intake

Resolve or conservatively declare:

1. agent objective, owned outcome, and intended caller/user;
2. operating surface and target hosts;
3. required inputs/context and expected outputs;
4. capability/tool contract (`required | optional | conditional | forbidden`);
5. authority boundary (`may decide | may recommend | may execute | must not execute | must escalate`);
6. exposed capabilities, downstream permissions, approval scope, and resulting effective authority when execution is possible;
7. context contract: isolation/inheritance mode, provenance/trust, freshness, sensitive-data rules, retrieval/compaction;
8. state, interrupted states, resume preconditions, terminal states, retry/re-entry, and termination behavior when stateful;
9. stop conditions and human/supervisor triggers;
10. control-flow/handoff topology when multiple actors exist;
11. concurrency/write-conflict policy when multiple actors can mutate overlapping resources;
12. validation scenarios, evaluator identity, and evidence status.

Ask a follow-up only when missing information changes a safety/authority boundary or makes the requested artifact impossible. Otherwise use conservative assumptions and label them.

## Multi-Agent Admission Gate

Before introducing multiple agents, require at least one material reason:

- independent work can run in parallel;
- context isolation prevents pollution or excessive context growth;
- authority isolation separates review/approval from mutation/execution;
- different tools/capabilities require genuinely different operators;
- independent verification materially improves confidence;
- distinct domain/output ownership creates a real boundary.

If none applies, prefer one bounded agent, a Skill, or a deterministic workflow. More agents are not a quality signal.

## Progressive Loading

Load only what the active mode needs:

- `references/agent-contracts.md`: canonical `agent-design-contract/v2`, effective authority, capability, context, control-flow, state/completion, evidence, and `handoff/v2` semantics.
- `references/agent-design-rubric.md`: `agent-design-rubric/v3`, critical gates, severity, advisory scoring, archetypes.
- `references/agent-governance-patterns.md`: least/effective authority, containment, blast radius, downstream authorization, controlled execution, audit/rollback.
- `references/routing-and-handoff-patterns.md`: deterministic routing, `delegate-return | transfer-control | suggested-transition | parallel-child`, handoff payloads, cycle and concurrency safety.
- `references/context-state-and-concurrency.md`: context trust/provenance, interruption/resume, concurrent mutation, and state freshness.
- `references/host-adapters.md`: portable capability model and host-specific adaptation rules for OpenAI/Codex/Claude/Copilot/VS Code/Visual Studio/Cursor.
- `references/agent-validation-scenarios.md`: `agent-eval-contract/v2`, frozen scenario/evaluator identity, outcome/trace checks, trials/reliability, baseline/candidate comparison.
- `evals/agent-design-scenarios.json`: frozen planned scenario suite for this skill; do not call it executed evidence until a harness actually runs it.
- `assets/templates/agent-spec.md.template`: reusable durable agent specification.
- `assets/templates/agent-review-report.md.template`: structured review/governance report.

## Workflow

1. Select mode, operating surface, and target hosts.
2. Run intake and state assumptions/evidence strength.
3. Determine Skill-vs-Agent ownership and the exact agent-owned outcome.
4. Define mission, responsibilities, non-responsibilities, declared authority, capabilities, and effective-authority evidence.
5. Define the context contract and trust boundary.
6. For stateful work, define active/interrupted/terminal transitions, resume preconditions, retry/re-entry, and failure behavior.
7. For multi-agent work, pass the admission gate, then define control-flow kind, ownership transfer/return semantics, `handoff/v2`, fallback, cycle safety, and concurrency policy.
8. For high-impact work, define blast radius, containment, downstream authorization, approval granularity, resource/budget limits, validation, and rollback/compensation.
9. Draft the prompt/spec/host-adapted agent artifact when requested.
10. Run governance review using critical gates from `agent-design-rubric/v3` before any advisory score.
11. Define validation using `agent-eval-contract/v2`; label scenarios `planned | executed | supplied` and never convert static structure into behavioral proof.
12. When a file artifact is available, run the structural validator; keep structural, behavioral, runtime, and semantic-review claims separate.
13. Deliver the requested artifact plus only the evidence, risks, and limitations needed to interpret it.

## Effective Authority

Represent authority in layers:

- **declared authority**: what the spec/prompt says the agent may decide/execute;
- **exposed capabilities**: tools/resources the host actually makes reachable;
- **downstream authority**: permissions enforced by repositories/APIs/services/credentials;
- **approval scope**: any additional operation-specific authorization;
- **effective authority**: actions actually possible after the above constraints intersect.

Required invariant for controlled designs:

`effective_authority <= declared_authority`

If the host default, tool exposure, or downstream permissions are unknown and could broaden a read-only/review/router/governance role, mark the authority gate `blocked/incomplete`; do not infer safety from omitted configuration.

## Multi-Agent State, Interruption, and Termination

For routers, supervisors, delegated execution, repair loops, or re-entrant workflows:

- declare who owns orchestration state and the top-level outcome;
- declare control-flow kind and whether ownership transfers or returns;
- distinguish active, interrupted, and terminal states;
- define interruption reasons such as `input-required`, `auth-required`, or `approval-required` when applicable;
- require resume preconditions and revalidate authorization/context freshness before resuming;
- define terminal outcomes (`completed`, `failed`, `canceled`, `rejected`, `blocked/escalated`, or a justified subset);
- forbid repeated materially identical handoffs;
- require a material state change for re-entry;
- define a finite loop/hop/repair bound or equivalent terminating predicate;
- if no loop policy is specified, default to **no cyclic re-entry**;
- prevent workers from recursively delegating unless that responsibility is explicit;
- if parallel writers can touch overlapping resources, require single-writer ownership, resource partitioning, locking, isolated worktrees/environments, or an equivalent conflict-control mechanism.

## Host Adaptation

Design the portable contract first. Then load `references/host-adapters.md` and map semantic capabilities/control-flow to the requested host.

For read-only/review/router/governance agents, prefer an **explicit restrictive tool list** rather than relying on omitted-tool defaults. Tool omission can mean broad access on some hosts. If the host's exact semantics are unknown, emit the portable spec and mark host adaptation `blocked` rather than inventing frontmatter/tool names.

Do not copy a VS Code/GitHub/Cursor tool name into the portable core. Host-specific file paths, frontmatter, MCP fields, and delegation primitives are adapters.

## Reproducibility and Evidence

Use the evidence vocabulary from `agent-design-contract/v2`:

- `measured`: executed validator/scenario/runtime evidence;
- `observed`: directly inspected artifact/source;
- `supplied`: externally provided evidence;
- `inferred`: reasoned conclusion;
- `planned`: not executed;
- `blocked`: unavailable.

Keep structural, behavioral, runtime, and semantic-review evidence separate. A valid Markdown shape does not prove agent behavior; a planned scenario does not prove validation.

For comparisons or reliability claims, freeze scenario/evaluator identities before candidate changes when feasible. Use repeated trials only when the claim depends on stochastic reliability; do not add trial machinery to static checks.

For generated files, run when possible:

```text
<PYTHON> scripts/validate_agent_artifact.py <ARTIFACT> --kind auto --profile <PROFILE> --json <RECEIPT>
```

For this skill package itself:

```text
<PYTHON> scripts/validate_agent_design_package.py --target <SKILL_ROOT> --json <RECEIPT>
```

The validators emit machine-readable structural evidence and intentionally do not claim semantic or runtime correctness.

## Output Contracts

### Agent design

Return, as applicable:

1. name, operating surface, target hosts, contract identity, and owned outcome;
2. objective/users, inputs/context, and outputs;
3. declared/effective authority and capability contract;
4. context contract and trust/freshness rules;
5. state/interruption/resume/termination and stop/escalation behavior;
6. complete prompt or host-adapted agent artifact when requested;
7. control-flow/handoffs, concurrency, and cycle rules when relevant;
8. containment/downstream authorization for high-impact work;
9. validation scenarios/evaluator identity and evidence status;
10. material risks/trade-offs/assumptions.

### Agent review

Return:

1. verdict from critical-gate rules;
2. critical gates with evidence labels;
3. findings using stable severity and criterion/evidence/fix mapping;
4. effective-authority/tool/context/state/control-flow/containment assessment as applicable;
5. concrete required fixes;
6. validation plan and explicit not-measured items.

### Repository structure review

Return:

1. detected structure/host;
2. ownership and placement findings;
3. naming/frontmatter/authority/tool issues;
4. duplication among agents/prompts/instructions/Skills;
5. routing/cycle/termination/concurrency issues;
6. bounded migration/cleanup plan.

## Stop Conditions

Stop or return a blocker when:

- the request belongs to Skill-package creation/improvement rather than agent design;
- high-impact autonomy lacks explicit authority, containment, or downstream authorization;
- effective authority cannot be bounded for a role that must be read-only or otherwise restricted;
- required ownership or operating surface is unresolved and changes safety/correctness;
- a router would need to execute specialist responsibilities without an explicit manager/worker redesign;
- a stateful topology has no safe interruption/resume/termination contract;
- a multi-agent design has no material admission reason;
- parallel writers lack a safe conflict-control strategy;
- a required capability is unavailable and no valid fallback/handoff exists;
- the request requires hidden, unaudited, self-modifying, policy-bypassing, or uncontrolled behavior;
- measured validation is requested but no executed evidence exists.

## Final Validation and Freeze

Before calling a design ready:

- Skill-vs-Agent fit and owned outcome are explicit.
- Critical gates pass or the result is correctly `blocked/reject/approve with changes`.
- Effective authority is explicit and does not exceed declared authority.
- Context cannot grant authority and has provenance/trust/freshness rules when material.
- Stateful/multi-agent designs have interruption/resume, termination, cycle safety, and concurrency control where applicable.
- Control-flow ownership is explicit; `handoff/v2` is compact and versioned when structure matters.
- High-impact designs bound blast radius and rely on downstream authorization rather than model judgment alone.
- Validation covers activation/non-activation, ambiguity, core, edge/failure, regression, and adversarial behavior as relevant.
- Evidence claims match what was actually executed/observed/supplied.
- Structural validators pass when applicable.

After the final validation pass, the artifact is the **frozen candidate**. Do not make unvalidated edits after pass; any material edit invalidates the affected evidence and requires revalidation.
