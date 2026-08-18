# Execution Profiles

Execution profiles control evidence depth, validation breadth, records, and rollback. They are orthogonal to source modes: ADHOC, RALPH, and ADAPT describe where work comes from; `quick`, `standard`, and `governed` describe how much control the risk requires.

## Selection

Select the lowest profile that satisfies every detected risk. Escalation is automatic and one-way during a run. A caller may request a higher profile, never a lower one than the risk matrix permits.

| Profile | Intended work | Minimum evidence | Success checks | Documentation | Rollback | Run record |
|---|---|---|---|---|---|---|
| `quick` | localized, reversible, low-risk change with a clear target and safety net | inspected target, requested behavior, changed-file list, one relevant check | targeted test/check plus package or syntax validation when applicable | concise changed/validated/gaps response; durable notes only when execution records changed | direct file revert or equivalent explicit undo | optional unless interrupted, RALPH-controlled, or stateful |
| `standard` | normal feature, bug, refactor, or multi-file change | context map, affected contracts, changed-file-to-check mapping, command evidence | targeted checks, build/lint/type checks that apply, regression test, closure review | implementation notes and validation evidence when durable records are useful | bounded rollback steps and dependency order | required for multi-step or resumable work |
| `governed` | migration, public contract, security, compliance, cross-service, multi-repository, destructive, or high-risk change | complete requirement/task/file/check/evidence traceability; risk classification; compatibility and operational evidence | all selected checks from the risk matrix, convergence gate, rollback verification, operational checks when triggered | implementation and validation records plus only the triggered migration, contract, security, observability, runbook, or troubleshooting artifact | tested or mechanically verifiable rollback/forward-fix plan with stop conditions | required, machine-readable, drift-checked |

## Automatic Escalation

Escalate to `standard` when any of these apply:

- more than one behavior-bearing file or component changes;
- the work lacks a direct targeted safety net;
- state, concurrency, messaging, caching, performance, or shared configuration is affected;
- interruption or multi-step execution is plausible;
- the requested output includes durable execution records.

Escalate to `governed` when any of these apply:

- schema or data migration, destructive operation, irreversible transform, or complex rollback;
- authentication, authorization, secrets, PII, compliance, or security posture;
- public API, event, file, schema, interface, or consumer contract;
- infrastructure, deployment sequencing, cross-service, or multi-repository rollout;
- material availability, data-loss, financial, legal, or regulatory risk;
- a planning gap changes intent, acceptance criteria, public behavior, persistence, or architecture.

`quick` never bypasses secret scanning, authorization review, data-loss checks, migration checks, or public-contract checks. Detection of one of those risks immediately changes the profile to `governed` before mutation continues.

## User-Facing Lifecycle

Every profile uses the same lifecycle:

```text
inspect -> execute -> validate -> converge -> close
```

- **inspect**: resolve mode, profile, scope, source truth, risks, writes, and success checks.
- **execute**: apply the smallest sufficient change and checkpoint meaningful steps.
- **validate**: run checks selected from actual changed surfaces and risk classes.
- **converge**: compare requirements, acceptance criteria, tasks, changed files, checks, and evidence.
- **close**: synchronize permitted records, state residual risk, and report only current evidence.

## Output Depth

- `quick`: changed, validation, gaps. Omit empty sections and operational detail.
- `standard`: mode/profile/scope, changes, validation, decisions, risks, rollback.
- `governed`: standard output plus traceability status, operational artifacts, compatibility, rollback evidence, handoffs, and unresolved stop conditions.

Do not expand small-work output merely to expose internal mechanics. Machine-readable records may retain complete evidence while the human response references them concisely.
