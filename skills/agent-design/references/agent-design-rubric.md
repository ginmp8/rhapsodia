# Agent Design Rubric

Rubric identity: `agent-design-rubric/v3`.

Evaluate critical gates before advisory scoring. A high aggregate score never hides unsafe authority, undefined control flow, unbounded execution, or misleading evidence.

## Skill vs Agent Fit

Prefer a Skill for standardized competency, fixed validators/templates, or packaged repeatable workflow. Prefer an Agent for mission ownership, state, routing, supervision, governance, controlled execution, or explicit coordination across actors/tools. Use a mixed system when an Agent coordinates reusable Skills without copying them.

## Critical Gates

Score applicable gates `0 fail | 1 incomplete | 2 pass | 3 strong pass`; use `N/A` only with rationale.

| Gate | 0 - fail | 1 - incomplete | 2 - pass | 3 - strong pass |
|---|---|---|---|---|
| Mission/ownership | no owned outcome | broad/overlap | clear owned outcome | explicit conflict boundary |
| Effective authority | implicit/unbounded or exceeds declared | declared only; exposure/downstream unknown | declared/exposed/downstream/approval reconcile | least privilege plus delegation inheritance proven |
| Tool least authority | unjustified high-impact/broad tools | tool defaults ambiguous | minimal explicit capabilities | minimal capabilities plus verified fallback/conditional gates |
| Context trust/authority | context can override/grant authority | sources/trust/freshness partial | context contract and authority invariant | retrieval/compaction/sensitive data/freshness all bounded |
| Control-flow ownership | ambiguous handoff ownership | kind or return semantics partial | transition kind and ownership explicit | ownership plus fallback/trace semantics explicit |
| Multi-agent admission/concurrency | unnecessary topology or unsafe overlapping writers | benefit/control partial | justified topology and safe writer strategy | isolation/integration/cycle controls explicit |
| Stop/escalation | absent for material risk | generic | concrete stop/escalation | tied to state/evidence/authority |
| State/interruption/termination | unbounded/cyclic or unsafe resume | partial terminal/resume semantics | terminal + interrupted + resume/re-entry rules | scope/freshness revalidation and finite loop controls explicit |
| Containment/downstream auth | high-impact action relies on model/approval only | containment or downstream auth partial | blast radius + downstream authorization + recovery | layered containment, limits, validation, compensation, audit |
| Evidence truthfulness | planned/supplied presented as measured | evidence labels incomplete | layers/statuses correct | evaluator identity and claim limits explicit |

Applicability:

- stateless single-turn agents may mark state/interruption `N/A`;
- single-agent designs may mark control-flow and multi-agent gates `N/A`;
- containment/downstream-auth is required for high-impact execution and otherwise may be `N/A`;
- `N/A` must not hide an actually present risk surface.

### Verdict rules

Apply in order:

1. `blocked`: required input/owner/authority/capability/evidence cannot be established safely.
2. `reject`: any applicable critical gate is `0`, or requested behavior is hidden, uncontrolled, policy-bypassing, unauditable, or unsafe and cannot be redesigned in scope.
3. `approve with changes`: no gate is `0`, but any applicable gate is `1` or an unresolved `high` finding remains.
4. `approve`: all applicable gates are at least `2` and no unresolved `critical/high` finding remains.

## Advisory Quality Score

After hard gates, optionally score `0..3`:

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Mission | vague | broad | clear | success criteria included |
| Responsibilities | generic | partial | concrete | sequenced/owned |
| Non-responsibilities | absent | generic | concrete | exclusions tied to escalation |
| Inputs/context | unknown | examples | required inputs | trust/freshness/retrieval bounded |
| Outputs | unspecified | prose | structured | acceptance bar |
| Authority | absent | declared only | effective authority reconciled | delegation/containment integrated |
| Tools/capabilities | absent | broad/defaulted | minimal explicit | fallback/conditional/host mapping |
| Control flow | absent | informal | kind/target/return | versioned compact contract + fallback |
| State/concurrency | absent | partial | termination/interruption or writer policy | re-entry/freshness/isolation robust |
| Validation/evidence | absent | checklist only | scenarios/labels | frozen evaluator + outcome/trace contract |

Do not compare totals if scored dimensions differ materially.

## Severity Taxonomy

- `critical`: uncontrolled high-impact action, destructive/credential/security boundary violation, authority amplification, unbounded execution with material impact, or evidence/authorization bypass.
- `high`: likely scope/authority overreach, unsafe tool exposure, wrong-owner control transfer, missing termination/resume protection, unsafe parallel mutation, or missing downstream authorization for meaningful actions.
- `medium`: bounded ambiguity likely to create inconsistent behavior, incomplete outputs, context loss, or avoidable manual correction.
- `low`: clarity, maintainability, portability, or documentation defect with limited behavioral impact.

Severity follows failure impact/reach, not prose quality.

## Evidence Labels

Use the `agent-design-contract/v2` vocabulary: `measured | observed | supplied | inferred | planned | blocked`.

A finding must connect criterion -> evidence -> failure mechanism -> required fix. Distinguish observed defect from inferred risk.

## Prompt Quality Requirements

A strong agent prompt/spec includes, when applicable:

1. mission/owned outcome;
2. trigger/operating context;
3. responsibilities/non-responsibilities;
4. declared and effective authority assumptions;
5. explicit capability/tool contract;
6. context trust/freshness rules;
7. workflow;
8. state/interruption/resume/termination;
9. control-flow/handoffs/concurrency;
10. output contract;
11. stop/escalation;
12. containment/downstream authorization for high impact;
13. validation expectations/evidence labels.

Avoid persona-heavy prose, broad autonomy, duplicated specialist instructions, hidden-reasoning requirements, assumed tools, unbounded delegation, and prompt-only authorization.

## Tool Contract Defaults

| Agent type | Default capability posture | Escalation before adding |
|---|---|---|
| Router | no tools or explicit read-only context | any write/process/deployment/specialist execution |
| Governance/review | explicit read/search | mutation, execution, approval on behalf of a human |
| Planner/designer | explicit read/search; artifact creation when requested | repository-wide edits/runtime execution |
| Controlled executor | scoped edit/test | deployment, secrets, destructive action, production operation |

Omitted host tool configuration is not a safe portable default for restricted roles.

## Common Archetypes

### Router
Classifies, selects target, emits compact `handoff/v2`, and stops. It does not perform specialist execution.

### Manager/Supervisor
Retains top-level ownership and delegates bounded subtasks via `delegate-return`/`parallel-child`. It must define child authority/context and integration rules.

### Governance/Review Agent
Owns inspection, policy/authority review, and escalation. Mutation requires a different explicit authority contract.

### Controlled Executor
Owns bounded change with preconditions, containment, allowed/blocked scope, validation, failure handling, and rollback/compensation.

### Prompt/Agent Designer
Converts requirements into agent contracts/instructions and host adapters. It does not perform the downstream mission merely because it can describe it.
