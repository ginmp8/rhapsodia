---
name: modern-dotnet-engineering
description: use for c#/.net 10 software engineering guidance, code review, architecture, implementation planning, refactoring, production readiness, security, performance, minimal apis, ef core 10, async, http resilience, messaging, dependency and nuget governance, testing, containers, aspire, native aot, observability, compliance, or .net ai/agent/mcp engineering. assume net10.0, c# 14, asp.net core 10, and ef core 10 as the stable baseline unless the user explicitly says otherwise. do not use for non-.net work, generic writing, artifact formatting, or stack-agnostic architecture questions that do not materially depend on .net.
---

# Modern .NET Engineering

## Purpose

Produce practical, production-oriented C#/.NET guidance. Optimize for explicit behavior, current supported .NET servicing, secure defaults, bounded complexity, observable operations, reproducible builds, and evidence-based review. Prefer the simplest complete design that satisfies the actual requirement.

## Activation contract

Activate when the primary task materially depends on C#, .NET, ASP.NET Core, EF Core, runtime/SDK behavior, NuGet/project structure, .NET testing/deployment, Native AOT, Aspire, or .NET-specific AI/agent/MCP engineering.

Do not activate for non-.NET implementation, generic writing/artifact work, stack-agnostic architecture, or cloud/database/security/AI/MCP/frontend questions where .NET-specific behavior would not change the answer. If the stack is unspecified and runtime choice is material, do not silently force .NET. Load AI/agent/MCP guidance only when model APIs, agents, RAG, tool execution, or MCP are actually in scope.

## Baseline assumptions

- Default to stable `net10.0`, C# 14, ASP.NET Core 10, and EF Core 10 unless the user/repository specifies another target. Reverify lifecycle, current servicing patch, prerelease status, or security facts when freshness matters; previews/RCs never silently replace the stable/requested baseline.
- Preserve repository policy for nullable references, implicit usings, central package management, analyzers, warnings-as-errors, lockfiles, SDK selection, and deployment model.
- Prefer Minimal APIs for new bounded HTTP surfaces unless Controllers solve a concrete requirement better.
- Prefer a modular single deployable with explicit boundaries before Clean Architecture, CQRS/mediator, DDD ceremony, distributed messaging, microservices, caching, reflection-heavy infrastructure, Aspire, Native AOT, or new abstractions.
- Treat authorization, resource limits, idempotency, observability, graceful shutdown, secrets, dependency risk, migrations, compatibility, and rollback/forward recovery as production concerns, not optional polish.

## Mode router

Choose exactly one primary mode:

| Mode | Select when |
|---|---|
| `quick-guidance` | focused question, API/version/lifecycle choice, or concise recommendation |
| `code-review` | concrete code, diff, repository, PR, stack trace, or implementation is inspected |
| `architecture-design` | boundaries, dependencies, data flow, scalability, distribution, or system shape are central |
| `implementation-plan` | sequencing, file layout, migration/refactor steps, or execution planning is requested |
| `production-gate` | production readiness, security, deployability, or supportability needs a verdict |

Precedence: go/no-go -> `production-gate`; concrete artifact findings -> `code-review`; execution sequence -> `implementation-plan`; design decision -> `architecture-design`; otherwise -> `quick-guidance`. Mixed requests keep one primary mode and only the necessary secondary sections.

## Core workflow

1. Establish target identity and relevant evidence: repository/file/revision, SDK/runtime/TFM, framework/provider/package versions, deployment model, constraints, and repository instructions.
2. Verify current official sources for freshness-sensitive lifecycle, support, security, package, Native AOT, or framework-behavior claims.
3. Load only the directly relevant references; never load the whole knowledge base for a focused question.
4. Apply `references/35-decision-matrix.md` before adding patterns, dependencies, layers, caches, mediators, queues, distributed boundaries, Aspire, Native AOT, or AI/MCP infrastructure.
5. Separate evidence from inference with `references/36-review-evidence-and-reproducibility.md`; source/SDK/package/provider/runtime identity is part of the evidence boundary when it can change behavior.
6. Prefer the smallest complete change that preserves existing contracts unless the request explicitly includes migration/breaking change work.
7. Validate bottom-up: restore/build -> focused tests -> analyzers/security/dependency checks -> provider/runtime smoke -> performance/load evidence -> production telemetry. Earlier layers never prove later ones.
8. When required evidence is missing, use `blocked` or `planned`; never convert uncertainty into a pass.

## Global rules

- Keep business rules out of endpoints/controllers, EF configuration/migrations, infrastructure adapters, Aspire ServiceDefaults, and model prompts when an application/domain model exists; do not expose EF entities directly from public APIs.
- Propagate `CancellationToken` through I/O/long-running work unless a boundary explicitly owns cancellation. Treat `DbContext` as scoped, short-lived, and not thread-safe; query filters are data-scope conveniences, never the sole authorization boundary.
- Prefer deployment-controlled migrations for important systems; startup migration needs explicit concurrency, privilege, and deployment justification.
- Never log secrets, tokens, cookies, private keys, full connection strings, unnecessary PII, or sensitive prompt/tool content. Prefer identity-based access and managed secret stores over long-lived static credentials.
- Retries require operation-semantic justification; state-changing operations need idempotency or equivalent protection. Use outbox/dead-letter/retry limits when the failure model requires them, and bounded queues/channels with explicit backpressure when producers can outrun consumers.
- Treat model output/tool arguments as untrusted input. Authorization, schema validation, tenant/resource checks, and destructive-action controls must remain executable code/policy outside prompts.
- Preserve public contracts, migrations, package policy, architecture boundaries, tests, analyzers, audit/security controls, and compatibility requirements unless the requested change explicitly owns their migration/impact.
- Do not add generic repositories, CQRS/mediator, DDD ceremony, caching, eventing, microservices, Aspire, Native AOT, source-generation-heavy infrastructure, or AI/MCP abstractions without a concrete need supported by the decision matrix.

## Direct reference map

Load only the branch that changes the decision. Every required Markdown reference is directly reachable from this file; cross-links inside references are navigation aids, not mandatory discovery hops.

- **Runtime/language:** lifecycle and SDK `references/03-dotnet-10-baseline.md`; C# types `references/04-csharp-14-type-modeling.md`; async/cancellation `references/05-async-tasks-cancellation.md`.
- **Architecture/design:** system shape `references/02-solution-architecture.md`; abstraction pressure `references/22-abstractions-design-overengineering.md`; CQRS/DDD `references/23-cqrs-mediator-ddd.md`; anti-patterns `references/33-modern-antipatterns.md`.
- **Data/API/contracts:** EF/migrations `references/09-ef-core-10-persistence.md`; transactions/concurrency `references/10-transactions-concurrency-consistency.md`; ASP.NET Core APIs `references/11-aspnet-core-10-api-design.md`; Minimal APIs `references/12-minimal-apis-net10.md`; serialization/versioning `references/13-serialization-contract-versioning.md`.
- **Security/reliability/dependencies:** security/auth `references/15-security-auth-secrets-sensitive-data.md`; NuGet/supply chain `references/18-supply-chain-dependencies-cicd-scripts.md`; HTTP resilience `references/21-resilience-timeout-retry-circuitbreaker-ratelimit.md`; outbox/idempotency `references/24-events-outbox-idempotency.md`; messaging/backpressure `references/25-messaging-workers-background-services.md`.
- **Performance/operations/deployment:** observability `references/14-logging-observability-pii.md`; performance `references/19-dotnet-10-performance.md`; caching `references/20-caching.md`; build quality `references/27-build-analyzers-cicd-quality.md`; deployment/Aspire `references/28-deployment-containers-healthchecks-shutdown.md`; AOT/trimming `references/29-aot-trimming-reflection-source-generators.md`.
- **Testing/review/gates:** testing `references/26-testing-modern-tooling.md`; production readiness `references/34-production-readiness-checklist.md`; pattern decision gate `references/35-decision-matrix.md`; evidence/severity/reproducibility `references/36-review-evidence-and-reproducibility.md`.
- **AI/agents/MCP:** load `references/37-dotnet-ai-agents-mcp.md` only when model APIs, agents, RAG, tool execution, or MCP are actually in scope.

## Evidence vocabulary

For review, validation, security, performance, reliability, or production-readiness claims, use exactly one primary label:

- `executed`: directly run in the current work and outcome observed;
- `observed`: directly inspected in supplied code/config/output;
- `supplied`: result provided but not independently rerun;
- `inferred`: reasoned from evidence, not directly measured;
- `planned`: recommended check/change not executed;
- `blocked`: required evidence could not be obtained.

Never describe `planned`, `inferred`, or missing evidence as executed validation. Use `references/36-review-evidence-and-reproducibility.md` for severity, confidence, verdict, and stale-evidence rules.

## Stop conditions

Stop, narrow scope, or mark the affected evidence `blocked` when:

- required code/repository/file content is unavailable;
- material SDK/runtime/TFM/provider/package/deployment identity is unknown;
- a freshness-sensitive lifecycle/security/framework fact cannot be verified and the decision depends on it;
- a destructive database/API/contract change lacks migration, compatibility, rollback, or forward-recovery evidence;
- a security or production-readiness verdict needs tests/scans/runtime/telemetry evidence that is unavailable;
- repository instructions, package/lock policy, generated-file ownership, or dependency constraints are unknown and the proposed edit could violate them;
- Native AOT is requested while trimming/AOT support of the relevant framework/dependencies is unresolved;
- the only route to a positive verdict is weakening tests, analyzers, NuGet audit, security controls, validation, compatibility requirements, or evidence gates.

## Progressive reference loading

Load these files as needed:

| Topic | Reference |
|---|---|
| principles | `references/01-engineering-principles.md` |
| solution architecture / modular monolith / distributed costs | `references/02-solution-architecture.md` |
| .net 10 lifecycle, servicing, sdk baseline | `references/03-dotnet-10-baseline.md` |
| c# 14 and types | `references/04-csharp-14-type-modeling.md` |
| async/tasks/cancellation | `references/05-async-tasks-cancellation.md` |
| error handling | `references/06-error-handling-result-exceptions.md` |
| dependency injection | `references/07-dependency-injection-lifetimes.md` |
| configuration/secrets/options | `references/08-configuration-options-secrets-flags.md` |
| ef core 10 / migrations / query filters | `references/09-ef-core-10-persistence.md` |
| transactions/concurrency/retry interaction | `references/10-transactions-concurrency-consistency.md` |
| asp.net core api design / resource authorization / limits | `references/11-aspnet-core-10-api-design.md` |
| minimal apis / built-in validation | `references/12-minimal-apis-net10.md` |
| serialization/contracts | `references/13-serialization-contract-versioning.md` |
| logging/observability/pii/cardinality | `references/14-logging-observability-pii.md` |
| security / BOLA / property authorization | `references/15-security-auth-secrets-sensitive-data.md` |
| audit/compliance | `references/16-audit-compliance-traceability.md` |
| threat modeling | `references/17-threat-modeling-security-review.md` |
| nuget audit / supply chain / ci / scripts | `references/18-supply-chain-dependencies-cicd-scripts.md` |
| performance | `references/19-dotnet-10-performance.md` |
| caching | `references/20-caching.md` |
| httpclient / resilience / retry safety | `references/21-resilience-timeout-retry-circuitbreaker-ratelimit.md` |
| abstractions/design | `references/22-abstractions-design-overengineering.md` |
| cqrs/mediator/ddd | `references/23-cqrs-mediator-ddd.md` |
| events/outbox/idempotency | `references/24-events-outbox-idempotency.md` |
| messaging/workers/channels/backpressure | `references/25-messaging-workers-background-services.md` |
| testing / mtp / expected-test-count | `references/26-testing-modern-tooling.md` |
| build/analyzers/cicd quality | `references/27-build-analyzers-cicd-quality.md` |
| deployment/containers/aspire/health/shutdown | `references/28-deployment-containers-healthchecks-shutdown.md` |
| aot/trimming/reflection/source generators | `references/29-aot-trimming-reflection-source-generators.md` |
| time/timeprovider/faketimeprovider | `references/30-time-dates-clock-timezone.md` |
| docs/adrs/runbooks | `references/31-technical-docs-adrs-runbooks.md` |
| agent/skill governance | `references/32-agent-skill-governance.md` |
| anti-patterns | `references/33-modern-antipatterns.md` |
| production readiness | `references/34-production-readiness-checklist.md` |
| decision matrix | `references/35-decision-matrix.md` |
| review evidence, severity, confidence, reproducibility | `references/36-review-evidence-and-reproducibility.md` |
| .net ai / agents / mcp | `references/37-dotnet-ai-agents-mcp.md` |



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

Distinguish existing facts from proposed state. For every new dependency, layer, queue, cache, mediator, repository, service boundary, Aspire component, AOT requirement, or AI/MCP abstraction, identify the concrete problem it solves and the validation that would justify keeping it.

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

The first validator preserves the baseline package/content contract. The second validates activation/routing/evidence/scenario reproducibility controls and emits machine-readable diagnostics. Neither proves behavioral improvement; behavioral claims require executed scenarios from `evals/scenarios.json` against compared skill versions.

After the final validation pass, freeze the candidate bytes used for packaging. Any later edit invalidates the affected validation evidence and requires those gates to run again.
