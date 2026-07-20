# Execution Profiles and Unified Lifecycle

Load after `references/common-execution.md`. Select the strictest evidence-triggered profile before mutation, then map it to ADHOC, RALPH, ADAPT, bug-fix, refactor, or documentation. A caller may request stricter execution, never weaker execution.

## Profiles

| Profile | Trigger and minimum evidence | Checks, records, and rollback |
|---|---|---|
| `quick` | Localized, reversible, low-risk change; known files/behavior, allowed/blocked paths, and one proving check | Targeted test/equivalent; syntax/build only when applicable. Simple revert. Run-state optional unless interruption, automation, or multiple writes matter. No durable docs unless the change creates durable knowledge. |
| `standard` | Normal feature, bug, refactor, or repo-doc change; bounded scope, success criteria, affected components, and validation plan | Targeted tests plus applicable build/lint/static, regression, and convergence checks. Explicit rollback. Focused implementation/validation records when durable artifacts exist; run-state for multi-step/resumable work. |
| `governed` | Migration, public/API/event/schema contract, auth/authz, secrets/PII, compliance, infrastructure, cross-service/repo, concurrency, performance, data loss, distributed consistency, difficult rollback, or high operational risk; source contract, consumers, risk, compatibility, rollback, and evidence are known | Full risk-selected checks and convergence. Machine run-state, checkpoints, drift verification, rollback/handoff evidence, implementation/validation records, and only triggered migration/contract/security/operational/ADR docs. |

Any security, secret, PII, authorization, migration, persistence compatibility, public contract, infrastructure, cross-repository, data-loss, distributed-consistency, or rollback-complexity signal forces `governed`. `quick` never bypasses those checks.

## Lifecycle

```text
inspect -> execute -> validate -> converge -> close
```

1. **Inspect**: resolve profile/mode, scope, source truth, files/components, proving checks, blocked paths, risk, and run-state need.
2. **Execute**: make the smallest sufficient change; checkpoint writes; preserve compatibility; stop at authority/safety boundaries.
3. **Validate**: run risk-selected checks and record `pass`, `fail`, or `not_run` with reason.
4. **Converge**: link requirements/objective, criteria, tasks, files, checks, and evidence; hand planning changes to Mago.
5. **Close**: sync truthful records, rollback/handoff state, and concise evidence; complete only after required validation and convergence pass.

ADHOC, bug/refactor/simplification, and technical docs use the evidence-selected profile. RALPH defaults to `standard`; ADAPT defaults to `quick` for one safe conversion and `standard` for multiple/conflicting artifacts. Both escalate on governed risk; ADAPT is never an implementation shortcut.

## Output Budget

Use run-state as the machine summary when required; reference logs instead of copying them.

- `quick`: only **Changes**, **Validation**, and **Gaps**; omit empty sections and operational docs.
- `standard`: focused implementation/validation evidence; add decisions or rollback only when material.
- `governed`: complete traceability plus only risk-triggered operational artifacts.
- Always redact secrets, credentials, PII, tokens, keys, and sensitive logs.
