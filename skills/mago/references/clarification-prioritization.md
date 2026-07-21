# Clarification Prioritization

Use this reference when multiple assumptions, questions, or blockers compete for attention. It extends the clarification readiness contract without changing its stable record IDs or handoff rules.

## Priority order

Rank each unresolved record by this tuple, highest first:

1. **Handoff blocking**: open blockers, then high/critical assumptions or questions.
2. **Irreversibility**: data loss, public contract, security boundary, compliance, migration, or rollback uncertainty.
3. **Dependency fan-out**: number of requirements, decisions, tasks, validations, repositories, or consumers affected.
4. **Evidence deficit**: no source, stale source, conflicting source, or unverified repository assumption.
5. **Decision latency**: whether waiting prevents safe partial planning or only defers an optional artifact.

Severity alone does not determine order. A medium question that blocks five downstream decisions may precede a high question isolated to one optional detail.

## Question budget

- Ask at most three blocking questions in one interaction unless the user explicitly requests a full questionnaire.
- Group questions by the same owner or decision boundary.
- Do not ask again when the answer exists in the Nomia handoff, canonical package, repository evidence, or prior validated planning.
- State why each question matters and which `REQ`, `AC`, `DECISION`, `task`, `VAL`, artifact, or gate it affects.
- Continue with safe partial planning when unresolved facts do not change identity, authority, risk profile, public behavior, compatibility, migration, security, rollback, or validation.

## Resolution outcomes

| Outcome | Use when | Required record update |
|---|---|---|
| `resolved` | evidence answers the issue | status, resolution evidence, affected IDs |
| `assumption` | bounded planning can proceed with visible uncertainty | owner, severity, evidence, resolution condition, affected IDs |
| `blocker` | safe canonical intent or handoff is impossible | owner, severity, evidence gap, resolution condition, blocked gates |
| `deferred` | optional detail has no current consumer or trigger | rationale, revisit trigger, no false readiness claim |

## Impact statement

For every surfaced question, include a compact impact statement:

```text
QUESTION-007 — decision needed: event compatibility policy
Why now: blocks DECISION-003, task004, VAL-006, and contract-spec.md
Owner: platform architecture
Safe partial work: repository discovery and current-consumer inventory only
```

Do not convert missing governance authority into a technical assumption. Route owner, priority, due-date, stakeholder, roadmap, release, or business-risk decisions to Nomia.
