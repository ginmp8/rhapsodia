# Risk and Change Escalation

Load before mutation when work can affect contracts, data, security, compliance, availability, financial outcomes, or more than one repository/service. Use the smallest rigor that safely fits the change.

## Risk Profile

| Profile | Use when | Minimum evidence |
|---|---|---|
| `standard` | Local, reversible implementation with known boundaries and no governed trigger | Objective, bounded files/modules, observable validation, compatibility check, rollback reasoning |
| `governed` | Public API/event/schema change; migration or data-loss risk; authentication/authorization; secrets, PII, regulated or financial data; high availability; weak rollback; or multi-service/multi-repository coordination | Standard evidence plus compatibility/migration plan, security/privacy review, staged validation, observability/operations evidence, ownership/handoff, and executable rollback or recovery |

Escalate to `governed` when uncertain whether a trigger applies. Do not add ceremony unrelated to the actual risk.

## Evidence Precedence and Conflict Handling

Use evidence in this order:

1. current repository code, runtime output, tests, and executed commands;
2. the selected active board/spec contract;
3. current validated planning and governance artifacts;
4. explicit, labeled implementation assumptions.

When higher-priority evidence conflicts with product intent, acceptance criteria, task definition, planned architecture, or authority records, stop the affected mutation and hand off. Do not silently choose the easier source.

## Change Classification

Classify affected behavior and contracts as `preserved`, `added`, `modified`, or `removed`. For each `modified` or `removed` surface, identify consumers, compatibility impact, rollout/migration order, rollback or recovery, and validation evidence. Treat API, event, schema, file format, configuration contract, permission, and persisted-data changes as contract surfaces.

## Pre-Mutation Gates

Before editing:

1. resolve the target, allowed writes, blocked paths, and validation command;
2. select the risk profile and record applicable triggers;
3. identify public/consumer-facing surfaces and persisted-data effects;
4. define the smallest safe change and rollback/recovery path;
5. for governed work, require explicit compatibility, security/privacy, operations, ownership, and staged-validation evidence.

If a required governed input is absent, perform safe inspection or partial evidence collection only; do not invent the missing control.

## Closure Gates

Before completion:

- run the narrowest proof plus every applicable governed check;
- record passed, failed, not-run, and blocked checks separately;
- confirm compatibility, migration order, rollback/recovery, security/privacy, observability, and operator guidance when applicable;
- update MAGIA-owned execution evidence and controlled execution state only from current results;
- hand off material planning changes to Mago and delivery/governance decisions to nomia.

A high test count or static score does not override a failed security, compatibility, migration, rollback, authority, or evidence-integrity gate.
