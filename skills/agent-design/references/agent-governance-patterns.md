# Agent Governance Patterns

Use these patterns for authority, auditability, escalation, controlled execution, and failure handling. Apply them even when the runtime has no dedicated governance feature.

## Governance Principles

1. **Least authority**: grant only the decisions and capabilities required by the mission.
2. **Fail closed for high-impact ambiguity**: unresolved intent, ownership, permission, or evidence blocks high-impact execution.
3. **Separate review from execution**: a reviewer does not gain mutation authority because it found a defect.
4. **Make termination observable**: stateful work needs completed, blocked/escalated, and failure outcomes.
5. **Preserve auditability**: decisions, evidence, actions, validation, and handoffs remain inspectable.
6. **Minimize handoff data**: transfer only context required by the recipient.
7. **Do not assume tools**: declare semantic capabilities and host adapters separately.

## Authority Boundary Pattern

Define:

- may decide;
- may recommend;
- may execute;
- must not execute;
- must escalate.

For write, terminal, deployment, destructive, financial, security-policy, identity/access, credential, or production-impacting actions, missing authority is a blocker rather than implicit permission.

## High-Impact Actions

Examples include production changes, deployments, destructive file/data operations, security policy mutation, credential handling, financial actions, identity/access changes, broad repository rewrites, irreversible migrations, and cross-system automation.

A high-impact action requires an explicit approved authority contract. If the surrounding environment already supplies a controlled-execution authorization, record that dependency rather than inventing a second approval mechanism.

## Stop Conditions

Include the conditions relevant to the role:

- scope conflicts with the mission or prior authority;
- required input, owner, permission, or context is missing;
- requested action exceeds the tool contract;
- evidence is insufficient for an approval/rejection/migration/execution decision;
- validation fails and no bounded repair is authorized;
- operation would touch protected resources outside the declared scope;
- a handoff target is unavailable or would receive incomplete/unsafe context;
- the same state/handoff repeats without new evidence;
- a finite iteration/repair budget is exhausted;
- the user asks for hidden, unaudited, policy-bypassing, or uncontrolled behavior.

## Audit Trail Pattern

For review, governance, routing, or execution work, record as applicable:

1. request and owned outcome;
2. scope and assumptions;
3. evidence/context inspected;
4. decisions and criteria;
5. tools/actions/commands used;
6. changed or proposed artifacts;
7. validation results and evidence labels;
8. unresolved risks/blockers;
9. handoff target and `handoff/v1` payload;
10. final state: completed, blocked, escalated, or rollback-required.

If durable logs are unavailable, emit the audit summary in the final artifact or conversation.

## Controlled Execution Pattern

Use only when mutation/execution is part of the explicit role.

Required controls:

- allowed scope and blocked/protected paths;
- preconditions and authorization state;
- bounded execution plan;
- idempotency/retry expectations when repeated actions are possible;
- validation checks;
- failure behavior;
- rollback or compensation strategy when meaningful;
- final state and audit receipt.

Do not treat "best effort" as a rollback strategy for destructive or irreversible actions.

## Governance Review Checklist

- Mission and owned output are specific.
- Critical gates from `agent-design-rubric/v2` were assessed.
- Tool contract follows least authority.
- Authority names allowed, forbidden, and escalation actions.
- Stateful/routing workflows have explicit termination and cycle rules.
- Handoffs are compact and avoid unnecessary sensitive data.
- Evidence labels distinguish observed/measured from inferred/planned.
- Validation covers misuse, ambiguity, failure, and adversarial cases.
- The design does not promise unavailable tools or background execution.
- Review/router agents do not silently acquire specialist execution authority.
