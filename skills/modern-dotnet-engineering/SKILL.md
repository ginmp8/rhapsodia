---
name: modern-dotnet-engineering
description: use for c#/.net 10 software engineering guidance, code review, architecture, implementation planning, refactoring, production readiness, security, performance, minimal apis, ef core 10, async, dependency injection, caching, cqrs, mediator, ddd, messaging, ci/cd, aot, observability, compliance, or agent-safe engineering decisions. assume net10.0, c# 14, asp.net core 10, and ef core 10 as the baseline unless the user explicitly says otherwise. do not use for non-.net work, generic writing, or artifact formatting tasks.
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

## Workflow decision tree

1. Classify the request:
   - **quick guidance**: answer directly with rules, trade-offs, and concise examples.
   - **code review**: inspect the artifact, produce severity-ranked findings, and recommend minimal fixes.
   - **architecture design**: produce a bounded recommendation with dependencies, trade-offs, risks, and validation.
   - **implementation plan**: provide file layout, minimal code shape, sequencing, and tests.
   - **production readiness/security gate**: classify as approved, approved with reservations, or blocked.
2. Load only the reference files that match the request. Do not load all references for simple questions.
3. Apply the decision matrix before adding patterns or dependencies.
4. Separate what is known from assumptions. Do not claim performance, security, reliability, or production readiness without evidence or explicit reasoning.
5. Prefer the smallest change or design that satisfies the business need.

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

1. [severity | confidence] issue - evidence - impact - smallest fix

## What is good

- ...

## Suggested minimal change

```csharp
// only when a concrete patch or example is useful
```

## Validation

- executed: ...
- not executed: ...
- suggested: ...
```

Severity: `critical`, `high`, `medium`, `low`, `informational`.
Confidence: `high`, `medium`, `low`.

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

### Production/security gate
Use:

```markdown
## Verdict
approved | approved with reservations | blocked

## Blockers

## Required fixes

## Recommended improvements

## Validation gates

## Residual risk
```

## Global rules

- Do not put business rules in endpoints, controllers, EF configurations, migrations, or infrastructure adapters when an application/domain model exists.
- Do not return EF entities directly from public APIs.
- Do not introduce generic repositories, mediator, CQRS, DDD, outbox, caching, or eventing unless the decision matrix supports it.
- Always propagate `CancellationToken` through I/O and long-running operations.
- Treat `DbContext` as scoped, short-lived, and not thread-safe.
- Prefer structured logs; never log secrets, bearer tokens, cookies, private keys, full connection strings, or unnecessary PII.
- Prefer identity-based access and managed secret stores over long-lived static credentials.
- For external side effects after database writes, consider outbox, idempotency, retry limits, and dead-letter handling.
- For .NET 10 features, explain the concrete benefit and any readability, provider, migration, AOT, trimming, or operational risk.

## Templates

Use bundled templates only when producing durable outputs:

- `templates/code-review-response.md`
- `templates/architecture-review-response.md`
- `templates/minimal-api-endpoint.md`
- `templates/feature-slice.md`
- `templates/adr.md`
- `templates/pr-checklist.md`

## Validation script

When validating this skill package itself, run:

```bash
python scripts/validate_skill_content.py <skill-folder>
```

Then run the skill packaging validator.
