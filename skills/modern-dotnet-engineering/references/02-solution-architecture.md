# Solution Architecture

## Recommended structure

Use this shape for long-lived business systems:

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

## Dependency direction

```text
Api -> Application, Infrastructure, Contracts
Worker -> Application, Infrastructure, Contracts
Application -> Domain, Contracts
Infrastructure -> Application, Domain, Contracts
Domain -> no internal project dependencies
Contracts -> no internal project dependencies
```

## When to simplify

For small CRUD apps, keep fewer projects and organize by feature. Do not create Domain/Application/Infrastructure just to look architectural.

## When to split

Create a separate project when it protects a real boundary: domain purity, composition root, contracts shared with other services, workers, tests, or infrastructure adapters.

## Architecture tests

Add tests that enforce dependency direction. Block references from Domain to Infrastructure/Web and from Application to Web.
