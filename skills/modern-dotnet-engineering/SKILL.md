---
name: modern-dotnet-engineering
description: use for c#/.net 10 software engineering guidance, code review, architecture, implementation planning, refactoring, production readiness, security, performance, minimal apis, ef core 10, async, dependency injection, caching, cqrs, mediator, ddd, messaging, ci/cd, aot, observability, compliance, or agent-safe engineering decisions. assume net10.0, c# 14, asp.net core 10, and ef core 10 as the baseline unless the user explicitly says otherwise. do not use for non-.net work, generic writing, artifact formatting, or stack-agnostic architecture questions that do not materially depend on .net.
---

# Modern .NET Engineering

## Purpose

Use this skill to produce practical, production-oriented C#/.NET guidance. Optimize for clear code, explicit business behavior, modern .NET 10 features, observable operations, secure defaults, bounded complexity, and evidence-based review.

## Baseline assumptions

- Assume `net10.0`, C# 14, ASP.NET Core 10, EF Core 10, nullable reference types, implicit usings, central package management, and warnings-as-errors unless the user says otherwise.
- Prefer Minimal APIs for new HTTP APIs unless Controllers solve a concrete requirement better.
- Prefer simple, explicit designs before Clean Architecture, DDD, CQRS, mediator, caching, reflection, or new abstractions.
- Treat production concerns as first-class: authorization, idempotency, observability, graceful shutdown, secret handling, auditability, and validation.
- Do not optimize for older .NET versions unless the user asks for compatibility or migration.
- When exact build/runtime behavior matters, identify the SDK/runtime/package versions actually supplied by the repository or user instead of assuming that all .NET 10 environments are identical.

## Activation contract

Activate when the primary task materially depends on C#, .NET, ASP.NET Core, EF Core, .NET runtime behavior, .NET project/package structure, or production engineering decisions for a .NET system.

Do not activate for:

- non-.NET implementation work;
- generic writing or artifact-formatting tasks;
- stack-agnostic architecture where .NET-specific behavior would not change the answer;
- general cloud, database, security, or frontend questions with no meaningful .NET dimension.

Boundary rule: if the stack is unspecified and the recommendation would materially change by runtime/framework, do not silently force .NET. State the assumption only when low-risk and obvious; otherwise request the missing stack/version evidence.

## Mode router

Choose exactly one primary mode before answering:

| Mode | Select when |
|---|---|
| `quick-guidance` | focused question, concept, API choice, or concise recommendation |
| `code-review` | concrete code, diff, repository, PR, stack trace, or implementation is being inspected |
| `architecture-design` | boundaries, components, dependencies, data flow, scalability, or system shape are the main question |
| `implementation-plan` | the user wants sequencing, file layout, migration/refactor steps, or an execution plan |
| `production-gate` | the user asks whether code/system is production-ready, secure enough, deployable, or should be blocked |

Routing precedence when several appear applicable:

1. explicit production/security go-no-go request -> `production-gate`;
2. concrete artifact with requested findings -> `code-review`;
3. requested implementation sequence -> `implementation-plan`;
4. requested system/design decision -> `architecture-design`;
5. otherwise -> `quick-guidance`.

For mixed requests, keep one primary mode and add only the secondary sections needed to answer the request. Do not merge every output contract into one response.

## Core workflow

1. Establish the supplied target identity: repository/file/version/framework/provider and relevant constraints when available. For repository/file reviews, prefer an exact commit or immutable supplied snapshot when practical; if the source changes, treat earlier evidence as stale and re-baseline the affected conclusions.
2. Load only the references needed for the selected mode and topic. Do not load all references for simple questions.
3. Apply `references/35-decision-matrix.md` before adding patterns, dependencies, layers, caches, mediators, or infrastructure.
4. Separate evidence from inference using `references/36-review-evidence-and-reproducibility.md`.
5. Prefer the smallest complete change or design that satisfies the business need and preserves existing contracts unless change is explicitly requested.
6. Validate at the lowest reliable layer available: build/test/analyzer/runtime evidence before prose confidence.
7. For reviews and gates, stop escalating certainty when required evidence is missing. Mark it `blocked` or `planned`; do not convert absence of evidence into a pass.

## Progressive reference loading

Load these files as needed:

| Topic | Reference |
|---|---|
| principles | `references/01-engineering-principles.md` |
| solution architecture | `references/02-solution-architecture.md` |
| .net 10 baseline | `references/03-dotnet-10-baseline.md` |
| c# 14 and types | `references/04-csharp-14-type-modeling.md` |
| async/tasks/cancellation | `references/05-async-tasks-cancellation.md` |
| error handling | `references/06-error-handling-result-exceptions.md` |
| dependency injection | `references/07-dependency-injection-lifetimes.md` |
| configuration/secrets/options | `references/08-configuration-options-secrets-flags.md` |
| ef core 10 | `references/09-ef-core-10-persistence.md` |
| transactions/concurrency | `references/10-transactions-concurrency-consistency.md` |
| asp.net core api design | `references/11-aspnet-core-10-api-design.md` |
| minimal apis | `references/12-minimal-apis-net10.md` |
| serialization/contracts | `references/13-serialization-contract-versioning.md` |
| logging/observability/pii | `references/14-logging-observability-pii.md` |
| security | `references/15-security-auth-secrets-sensitive-data.md` |
| audit/compliance | `references/16-audit-compliance-traceability.md` |
| threat modeling | `references/17-threat-modeling-security-review.md` |
| supply chain/ci/scripts | `references/18-supply-chain-dependencies-cicd-scripts.md` |
| performance | `references/19-dotnet-10-performance.md` |
| caching | `references/20-caching.md` |
| resilience | `references/21-resilience-timeout-retry-circuitbreaker-ratelimit.md` |
| abstractions/design | `references/22-abstractions-design-overengineering.md` |
| cqrs/mediator/ddd | `references/23-cqrs-mediator-ddd.md` |
| events/outbox/idempotency | `references/24-events-outbox-idempotency.md` |
| messaging/workers | `references/25-messaging-workers-background-services.md` |
| testing | `references/26-testing-modern-tooling.md` |
| build/analyzers/ci | `references/27-build-analyzers-cicd-quality.md` |
| deployment/runtime | `references/28-deployment-containers-healthchecks-shutdown.md` |
| aot/trimming/reflection | `references/29-aot-trimming-reflection-source-generators.md` |
| time/clock | `references/30-time-dates-clock-timezone.md` |
| docs/adrs/runbooks | `references/31-technical-docs-adrs-runbooks.md` |
| agent/skill governance | `references/32-agent-skill-governance.md` |
| anti-patterns | `references/33-modern-antipatterns.md` |
| production readiness | `references/34-production-readiness-checklist.md` |
| decision matrix | `references/35-decision-matrix.md` |
| review evidence, severity, confidence, reproducibility | `references/36-review-evidence-and-reproducibility.md` |

## Evidence vocabulary

For review, validation, security, performance, reliability, or production-readiness claims, use one of:

- `executed`: directly run in the current work and outcome observed;
- `observed`: directly inspected in supplied code/config/output;
- `supplied`: result provided by the user or external system but not independently rerun;
- `inferred`: reasoned conclusion from evidence, not directly measured;
- `planned`: recommended check or change not executed;
- `blocked`: required evidence could not be obtained.

Never describe `planned`, `inferred`, or missing evidence as executed validation. Full rules are in `references/36-review-evidence-and-reproducibility.md`.

## Output contracts

### Quick guidance

Return:
1. recommendation;
2. when to use it;
3. when not to use it;
4. minimal C# example when useful;
5. one validation or review check.

### Code review

Use this structure:

```markdown
## Findings

1. [severity | confidence | evidence-label] issue - location/evidence - failure condition - impact - smallest fix

## What is good

- ...

## Suggested minimal change

```csharp
// only when a concrete patch or example is useful
```

## Validation

- executed: ...
- observed: ...
- supplied: ...
- planned: ...
- blocked: ...

## Residual risk

- ...
```

Use the stable severity and confidence rules from `references/36-review-evidence-and-reproducibility.md`. Findings must identify a concrete failure condition or violated contract; do not report style preference as a defect.

### Architecture or implementation plan

Use:

```markdown
## Assumptions

## Recommendation

## Proposed structure

## Dependency direction

## Implementation sequence

## Validation plan

## Risks and trade-offs
```

Distinguish existing facts from proposed state. For every new dependency, layer, queue, cache, mediator, repository, or pattern, identify the concrete problem it solves and the validation that would justify keeping it.

### Production/security gate

Use:

```markdown
## Verdict
approved | approved with reservations | blocked

## Evidence status

## Blockers

## Required fixes

## Recommended improvements

## Validation gates

## Residual risk
```

Apply the verdict rules in `references/34-production-readiness-checklist.md`. Missing evidence for a required gate is not equivalent to a passing gate.

## Global rules

- Do not put business rules in endpoints, controllers, EF configurations, migrations, or infrastructure adapters when an application/domain model exists.
- Do not return EF entities directly from public APIs.
- Do not introduce generic repositories, mediator, CQRS, DDD, outbox, caching, or eventing unless the decision matrix supports it.
- Always propagate `CancellationToken` through I/O and long-running operations unless a boundary intentionally owns cancellation semantics and that exception is explicit.
- Treat `DbContext` as scoped, short-lived, and not thread-safe.
- Prefer structured logs; never log secrets, bearer tokens, cookies, private keys, full connection strings, or unnecessary PII.
- Prefer identity-based access and managed secret stores over long-lived static credentials.
- For external side effects after database writes, consider outbox, idempotency, retry limits, and dead-letter handling when the failure model requires them.
- For .NET 10 features, explain the concrete benefit and any readability, provider, migration, AOT, trimming, compatibility, or operational risk.
- Preserve existing public contracts, migrations, package policies, and architectural boundaries unless changing them is part of the request and the migration/compatibility impact is addressed.

## Stop conditions

Stop, narrow scope, or explicitly mark evidence `blocked` when:

- the requested code/repository/file is not available and the answer depends on its contents;
- target framework, provider, deployment model, or package version is material but unknown;
- a destructive database/API/contract change lacks migration, rollback, or compatibility evidence;
- a security or production-ready conclusion requires tests/scans/runtime evidence that was not supplied or executable;
- repository instructions, lockfiles, central package rules, or generated-file ownership are unknown and the proposed edit could conflict with them;
- the only path to a positive verdict is to weaken tests, analyzers, security controls, validation, or compatibility requirements.

## Templates

Use bundled templates only when producing durable outputs:

- `templates/code-review-response.md`
- `templates/architecture-review-response.md`
- `templates/minimal-api-endpoint.md`
- `templates/feature-slice.md`
- `templates/adr.md`
- `templates/pr-checklist.md`

## Skill-package validation

When validating this skill package itself, run both validators:

```bash
python3 scripts/validate_skill_content.py <skill-folder>
python3 scripts/validate_reproducibility.py <skill-folder> --json <receipt.json>
```

The first validator preserves the legacy package contract. The second validates activation/routing/evidence/scenario reproducibility controls and emits machine-readable diagnostics. Neither proves behavioral improvement; behavioral claims require executed scenarios from `evals/scenarios.json` against the compared skill versions.

After the final validation pass, freeze the candidate bytes used for packaging. Any later edit invalidates the affected validation evidence and requires those gates to run again.
