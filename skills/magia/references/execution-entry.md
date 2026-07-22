# Execution Entry and Bounded Ambiguity

Load at the start of executable work. This reference improves orientation; it does not replace repository truth, Mago planning artifacts, MAGIA validators, execution evidence, or controlled state.

## Execution Start Card

Before mutation, derive a compact, non-authoritative card from current evidence:

| Field | Required content |
|---|---|
| Mode | `ADHOC`, `RALPH`, or `ADAPT` |
| Risk profile | `standard` or `governed`, with active triggers |
| Bounded scope | Repository/root, selected task when applicable, allowed writes, blocked paths |
| Objective | Narrow technical outcome; preserve product intent verbatim when supplied |
| Proving check | Narrowest observable check and its expected result |
| Current blockers | Missing or conflicting evidence only; do not use implementation effort as a blocker |
| Next safe action | Inspect, run readiness, reproduce, patch, validate, recover, or hand off |
| Handoff | `none`, `mago`, `nomia`, or `both`, with a concrete reason |

Omit fields that genuinely do not apply, but never omit scope, objective, proof, blockers, or next action before a non-trivial mutation.

## First Safe Action

Choose the first action that increases evidence without expanding authority:

1. inspect current code, contracts, tests, and repository conventions;
2. run a read-only validator or readiness check;
3. reproduce the failure with the narrowest available check;
4. collect missing execution evidence;
5. stop and hand off when the missing decision belongs to Mago or nomia.

Do not start with broad refactoring, dependency installation, destructive commands, state mutation, or speculative architecture.

## Underdefined Task Decision

Proceed conservatively only when all conditions hold:

- the technical objective can be derived from current repository behavior or an existing task/acceptance boundary;
- the change does not alter product intent, public behavior beyond the task, planned architecture, contract shape, persistence semantics, security posture, ownership, sequencing, or delivery commitments;
- one observable proving check can be defined without inventing acceptance criteria;
- the write scope remains bounded and reversible.

When proceeding, record the assumption, its evidence, the smallest chosen implementation, and the proving check.

Hand off to Mago when a missing decision changes requirements, acceptance criteria, task definition, sequencing, planned architecture, public contract, persistence model, cross-service behavior, or security posture. Hand off to nomia when the missing decision changes owner, business priority, due date, delivery status, stakeholder communication, release posture, or accepted business risk.

## Compact Completion View

Keep the final response scan-friendly while preserving durable evidence in MAGIA-owned artifacts:

- mode/profile and scope;
- changed files or artifacts;
- checks grouped as `pass`, `fail`, `blocked`, `skipped`, or `not-run`;
- plan deviations and implementation decisions;
- residual risk and rollback/recovery;
- next action or handoff.

Never compress distinct validation states into a generic success statement.
