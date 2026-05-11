# Agent Governance Patterns

Use these patterns to review or design agent safety, auditability, escalation, and controlled execution. Apply them even when the target runtime does not expose dedicated governance tools.

## Governance Principles

1. Least authority: give the agent only the tools and decision rights required by its mission.
2. Fail closed for high-impact ambiguity: pause or escalate when intent, scope, permissions, or evidence is unclear.
3. Separate policy from execution: governance agents review and recommend; execution agents apply bounded changes only when authorized.
4. Preserve auditability: require visible summaries of decisions, evidence, commands, changed files, and handoffs.
5. Keep controls explicit: boundaries, stop conditions, and escalation rules must live in the prompt or agent spec, not in unstated assumptions.
6. Avoid tool hallucination: describe required capabilities without assuming MCP, repository, terminal, browser, or external services exist.

## Authority Boundary Pattern

Define each agent's authority with this structure:

- May decide: decisions within role scope.
- May recommend: decisions requiring human or downstream approval.
- May execute: allowed concrete actions, paths, commands, or tool categories.
- Must not execute: forbidden actions and protected resources.
- Must escalate: triggers requiring user, owner, reviewer, or governance approval.

High-impact actions require explicit human confirmation unless the user's environment already provides an approved controlled-execution contract.

High-impact actions include production changes, deployments, destructive file operations, security policy mutation, credential handling, financial decisions, identity/access changes, irreversible data changes, broad repository rewrites, and cross-system automation.

## Stop Conditions

Every agent needs stop conditions. Include the conditions that match the role:

- scope is ambiguous or conflicts with prior instructions;
- required input, ownership, permission, or repository context is missing;
- requested action exceeds the tool contract or authority boundary;
- evidence is insufficient for an approval, rejection, migration, or execution decision;
- validation fails and no bounded fix exists;
- operation would touch secrets, credentials, production data, protected branches, generated evidence, or blocked paths;
- handoff target is unavailable or would receive incomplete context;
- user asks the agent to bypass controls, hide evidence, or operate unaudited.

## Audit Trail Pattern

For review, governance, and execution agents, require an audit summary containing:

1. request summary;
2. scope and assumptions;
3. inspected sources or context used;
4. decisions made and reasons;
5. tools or commands used, if any;
6. changed files or proposed changes, if any;
7. validation results;
8. unresolved risks;
9. handoff recipient and payload.

If the runtime cannot persist audit logs, the agent should still emit the audit summary in the conversation or final artifact.

## Governance Review Checklist

Use this checklist for `agent-governance-review`:

- Mission and trigger are specific.
- Tool contract follows least authority.
- Write, terminal, web, deployment, or external-system tools are justified.
- Authority boundary names allowed, forbidden, and escalation actions.
- Stop conditions are concrete and high-impact actions are gated.
- Handoffs preserve context but avoid unnecessary sensitive data.
- Audit expectations are visible and realistic for the runtime.
- Validation plan includes misuse, ambiguity, and failure cases.
- Agent does not promise unavailable tools or background execution.
- Router agents do not embed or duplicate specialist prompts.

## Controlled Execution Pattern

Use this only when the agent is allowed to change files, run commands, or perform multi-step execution.

Required controls:

- Scope: allowed files, directories, repositories, or systems.
- Blocked paths: secrets, credentials, generated evidence, `.git`, protected config, production assets, and user-declared read-only files.
- Preconditions: inputs, approvals, clean working state, or selected issue/spec.
- Execution plan: short sequence before mutation.
- Validation: commands or checks that must pass.
- Rollback: how to revert or report partial work.
- Final report: changed files, commands, results, risks.

## Governance Agent Output Shape

```markdown
# Agent Governance Review

## Verdict
approve | approve with changes | reject | blocked

## Critical Findings
- [severity] finding, evidence, impact, fix

## Authority Boundary
- may decide:
- may recommend:
- may execute:
- must not execute:
- must escalate:

## Tool Contract Assessment
...

## Stop Conditions
...

## Auditability
...

## Required Fixes
...

## Validation Plan
...
```
