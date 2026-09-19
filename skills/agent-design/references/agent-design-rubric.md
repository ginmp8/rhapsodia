# Agent Design Rubric

Rubric identity: `agent-design-rubric/v2`.

Use this rubric when designing or reviewing custom agents, prompts, authority boundaries, tool contracts, routing, handoffs, and agentic structures. The rubric deliberately separates **critical gates** from an advisory quality score so a strong score cannot hide an unsafe or undefined authority boundary.

## Skill vs Agent Fit

Prefer a Skill when the request is a standardized capability, repeatable workflow, fixed validator, template, rubric, or packaged competency.

Prefer an Agent when the request requires one or more of:

- mission-oriented operation with a named owner;
- stateful or multi-step execution;
- routing, supervision, governance, or controlled execution;
- coordination across agents, Skills, humans, or tools;
- explicit authority and termination semantics.

Use a mixed system when an Agent operates or routes to reusable Skills. Keep capability ownership in the Skill and operational coordination in the Agent.

## Critical Gates

Evaluate applicable gates before any aggregate score.

| Gate | 0 - fail | 1 - incomplete | 2 - pass | 3 - strong pass |
|---|---|---|---|---|
| Mission/ownership | no owned outcome | broad/overlapping ownership | clear owned outcome | clear ownership plus conflict boundary |
| Authority | absent or unsafe implicit authority | partial rights/prohibitions | may/may-not/escalate defined | decision and execution rights fully bounded |
| Tool least authority | unjustified high-impact tools | broad tools with weak limits | minimal required tools | minimal tools plus fallbacks/conditional gates |
| Stop/escalation | absent for material failure/risk | generic stop wording | concrete stop and escalation rules | rules tied to state, evidence, and authority |
| State/termination | unbounded or cyclic execution | termination partly defined | terminal states and retry/re-entry rules defined | loop/cycle safety and failure states explicit |
| Evidence truthfulness | planned/supplied evidence presented as measured | labels incomplete | evidence strength labeled correctly | structural, behavioral, runtime evidence clearly separated |

For stateless single-turn agents, state/termination may be `N/A`; document why. For non-routing agents, routing-specific checks may also be `N/A`.

### Verdict rules

Use these rules in order:

1. `blocked`: a required input, owner, authority decision, capability, or evidence source is unavailable, so a critical gate cannot be assessed safely.
2. `reject`: any applicable critical gate is `0`, or the requested role requires hidden, uncontrolled, policy-bypassing, or unauditable behavior that cannot be safely redesigned in scope.
3. `approve with changes`: no critical gate is `0`, but any applicable critical gate is `1`, or an unresolved `high` finding remains.
4. `approve`: all applicable critical gates are at least `2` and no unresolved `critical` or `high` finding remains.

An aggregate score never overrides these rules.

## Advisory Quality Score

After critical gates, optionally score each dimension from 0 to 3. This score supports comparison and prioritization; it is not a verdict engine.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Mission | vague | broad intent | clear objective | objective plus success criteria |
| Responsibilities | generic | partial | concrete | concrete and sequenced |
| Non-responsibilities | absent | generic | concrete exclusions | exclusions tied to escalation |
| Inputs/context | unknown | examples only | required inputs | required plus conservative defaults |
| Outputs | unspecified | prose only | structured output | structure plus acceptance bar |
| Authority | absent | implied/partial | explicit | explicit plus conflicts/escalation |
| Tools | absent | broad | minimal | minimal plus fallback/conditional rules |
| Handoffs | absent | informal | target/trigger/payload | versioned compact contract plus fallback |
| State/termination | absent | partial | terminal states defined | retry/re-entry/cycle behavior defined |
| Validation/evidence | absent | checklist only | scenarios and labels | scenarios plus acceptance and evidence separation |

Record `N/A` rather than forcing a score for an inapplicable dimension. Do not compare totals if the scored dimensions differ materially.

## Severity Taxonomy

Use stable severity labels for findings:

- `critical`: permits uncontrolled high-impact action, hidden bypass, irreversible/destructive behavior, credential/security boundary violation, or unbounded execution with material impact.
- `high`: likely causes scope/authority overreach, wrong-owner execution, unsafe tool use, missing termination for meaningful actions, or a handoff that can cause repeated/incorrect execution.
- `medium`: bounded ambiguity or contract weakness likely to create inconsistent behavior, incomplete outputs, or avoidable manual correction.
- `low`: clarity, maintainability, portability, or documentation defect with limited behavioral impact.

Severity is based on failure impact and reach, not wording quality.

## Evidence Labels

Use the evidence vocabulary from `agent-design-contract/v1`:

- `measured`
- `observed`
- `supplied`
- `inferred`
- `planned`
- `blocked`

A review finding should link the criterion to the supporting evidence and distinguish an observed defect from an inferred risk.

## Prompt Quality Requirements

A strong agent prompt includes, when applicable:

1. identity and mission;
2. trigger/operating context;
3. responsibilities and non-responsibilities;
4. authority boundary;
5. tool contract;
6. workflow;
7. state/termination behavior for stateful work;
8. routing/handoff rules for multi-agent work;
9. output contract;
10. stop/escalation conditions;
11. validation expectations and evidence labels.

Avoid persona-heavy prose, broad autonomy, duplicated specialist instructions, hidden-reasoning requirements, assumed tools, and unbounded delegation.

## Tool Contract Defaults

Classify each capability as `required`, `optional`, `conditional`, or `forbidden`.

| Agent type | Default capability | Escalation before adding |
|---|---|---|
| Router | no tools or read-only context | any write, terminal, deployment, or specialist execution |
| Governance/review | read/search | mutation, execution, approval on behalf of a human |
| Planner/designer | read/search; artifact creation when requested | repository-wide edits or runtime execution |
| Controlled executor | scoped edit/test | deployment, secrets, destructive actions, production operations |

Host-specific tool names are adapters, not the portable contract.

## Common Archetypes

### Router Agent
Owns classification, target selection, compact handoff, fallback, and stop. It does not execute specialist tasks.

### Governance Agent
Owns policy/authority review, auditability, escalation, and risk gates. It does not silently convert recommendations into execution authority.

### Review Agent
Owns inspection and findings. Mutation requires an explicitly different repair/executor authority contract.

### Controlled Execution Agent
Owns bounded changes with preconditions, allowed/blocked scope, validation, failure handling, and rollback/compensation expectations.

### Prompt/Agent Designer
Owns converting requirements into an agent contract and instructions. It does not perform the downstream mission merely because it can describe it.
