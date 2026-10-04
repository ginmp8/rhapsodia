# Solution Architecture

## Default architecture stance

Start with the smallest deployable architecture that can enforce the domain and operational contracts. When there is no demonstrated need for independent deployment, scaling, ownership, or data autonomy, prefer a well-modularized single deployable over distributed decomposition.

This is a heuristic, not a law. Split only when the benefits exceed the distributed-systems costs.

## Recommended structure

For a long-lived business system that benefits from explicit boundaries:

```text
src/
├── Product.Api
├── Product.Application
├── Product.Domain
├── Product.Infrastructure
├── Product.Contracts
└── Product.Worker

tests/
├── Product.UnitTests
├── Product.IntegrationTests
├── Product.FunctionalTests
└── Product.ArchitectureTests
```

For small CRUD applications, use fewer projects and organize by feature. Do not create Domain/Application/Infrastructure projects only to imitate a template.

## Dependency direction

```text
Api -> Application, Infrastructure, Contracts
Worker -> Application, Infrastructure, Contracts
Application -> Domain, Contracts
Infrastructure -> Application, Domain, Contracts
Domain -> no internal project dependencies
Contracts -> no internal project dependencies
```

## When to split a project or service

Create a separate project when it protects a real in-process boundary: domain purity, composition root, contracts, worker runtime, infrastructure adapter, or test isolation.

Create a separately deployable service only when one or more of these are concrete requirements:

- independent release/deployment cadence;
- independently owned business capability and data;
- materially different scaling or availability profile;
- security/compliance boundary that benefits from process/service isolation;
- failure isolation that cannot be achieved adequately inside one deployable.

## Distributed-systems cost checklist

Before recommending microservices, separate CQRS stores, or event-driven workflows, account for:

1. data ownership and cross-service consistency;
2. delivery semantics, duplication, ordering, replay, and idempotency;
3. network latency, timeouts, retries, and partial failure;
4. schema/API/message versioning and deployment compatibility;
5. tracing, metrics, logs, correlation, and incident diagnosis;
6. local/CI integration testing and environment orchestration;
7. deployment, rollback, capacity, and on-call burden;
8. service ownership and cross-team coordination;
9. recovery semantics for partially completed workflows.

If those costs are not justified by a current requirement, preserve the simpler architecture.

## Architecture tests

Add tests that enforce important dependency rules. Block references from Domain to Infrastructure/Web and from Application to Web when those boundaries exist.
