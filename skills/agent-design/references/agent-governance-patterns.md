# Agent Governance Patterns

Use these patterns for effective authority, containment, auditability, escalation, controlled execution, and failure handling. Apply them even when the runtime has no dedicated governance feature.

## Governance Principles

1. **Least effective authority**: minimize what the agent can actually do, not only what the prompt says.
2. **Complete mediation**: protected downstream operations perform their own authorization checks; do not delegate authorization decisions solely to the LLM.
3. **No delegation amplification**: child/recipient authority stays within the delegator's effective authority unless separately and explicitly expanded.
4. **Context is not authority**: tool/MCP/web/file/peer content cannot grant permissions or waive gates.
5. **Fail closed for high-impact ambiguity**: unresolved intent, ownership, permission, exposure, or evidence blocks execution.
6. **Separate review from execution**: finding a defect does not grant mutation authority.
7. **Bound blast radius**: containment and resource limits reduce damage even when supervision fails.
8. **Make interruption/termination observable**: paused, completed, blocked, and failed outcomes are distinguishable.
9. **Preserve auditability**: decisions, evidence, transitions, actions, validations, and handoffs remain inspectable.

## Effective Authority Pattern

Record:

- declared: `may decide | may recommend | may execute | must not execute | must escalate`;
- exposed capabilities;
- downstream permissions;
- approval scope;
- derived effective authority.

If a supposedly restricted host artifact omits tool exposure and the host default is broad/unknown, authority is not proven.

## High-Impact Governance Contract

Examples: production changes, deployments, destructive data/file operations, security-policy mutation, credential handling, financial actions, identity/access changes, broad repository rewrites, irreversible migrations, and cross-system automation.

Require as applicable:

- explicit approved authority;
- resource/system/path scope;
- containment boundary (sandbox/VM/worktree/account/network/egress boundary or equivalent);
- downstream authorization at action time;
- approval granularity for irreversible/high-risk steps;
- rate/budget/time/action limits;
- precondition and validation checks;
- idempotency/retry semantics;
- rollback/compensation;
- audit receipt/log.

Human-in-the-loop is one layer. Do not use repeated approval prompts as the only barrier when technical containment/authorization can bound the action more reliably.

## Blast-Radius Pattern

Describe worst credible impact if the agent is wrong or manipulated:

- resources reachable;
- data mutable/deletable;
- external systems callable;
- credential scope;
- network/egress reach;
- maximum action count/cost/time;
- reversibility.

Reduce blast radius before adding convenience capabilities. Prefer a constrained environment where safe unattended execution is possible over broad authority guarded only by frequent prompts.

## Approval Pattern

An approval must identify:

- actor granting it;
- exact operation/resource/scope;
- validity/expiry where material;
- whether it is one-shot or reusable;
- evidence recorded;
- action that must re-check it.

An `auth-required`/`approval-required` state is a request, not authorization itself.

## Stop Conditions

Include relevant conditions:

- scope conflicts with mission/authority;
- required input/owner/permission/context is missing;
- exposed capability exceeds declared boundary;
- downstream authorization fails or is unverifiable;
- requested action exceeds tool/resource/budget scope;
- evidence is insufficient for approval/rejection/migration/execution;
- validation fails and no bounded repair is authorized;
- operation touches protected resources outside scope;
- handoff target is unavailable or would receive unsafe context/authority;
- same state/handoff repeats without new evidence;
- finite iteration/repair budget is exhausted;
- interrupted task cannot satisfy resume preconditions;
- hidden, unaudited, policy-bypassing, or uncontrolled behavior is requested.

## Audit Trail Pattern

Record as applicable:

1. request/owned outcome;
2. scope/assumptions;
3. evidence/context inspected and trust/freshness;
4. declared/effective authority and approvals;
5. decisions/criteria;
6. tools/actions/commands used;
7. changed/proposed artifacts;
8. control-flow transitions/handoffs;
9. validation results/evidence labels;
10. unresolved risks/blockers;
11. final state: completed, interrupted, blocked, failed, escalated, or rollback-required.

If durable logs are unavailable, emit an audit summary in the final artifact/conversation.

## Controlled Execution Pattern

Use only when mutation/execution is explicit role authority.

Required controls:

- allowed scope and protected paths/resources;
- preconditions/authorization state;
- containment/blast-radius controls;
- bounded plan;
- idempotency/retry expectations;
- validation checks;
- failure behavior;
- rollback/compensation;
- final state and receipt.

Do not treat "best effort" as rollback for destructive or irreversible actions.

## Governance Review Checklist

- Mission/owned output specific.
- Critical gates from `agent-design-rubric/v3` assessed.
- Effective authority reconciled and no delegation amplification exists.
- Tool exposure explicit for restricted roles.
- Context trust/freshness/authority boundary defined when material.
- High-impact blast radius and downstream authorization bounded.
- Stateful/routing workflows have interruption/resume/termination/cycle rules.
- Parallel writers have conflict control.
- Handoffs are compact and avoid sensitive/unnecessary data.
- Evidence labels distinguish observed/measured from inferred/planned.
- Validation covers misuse, ambiguity, failure, and adversarial cases.
