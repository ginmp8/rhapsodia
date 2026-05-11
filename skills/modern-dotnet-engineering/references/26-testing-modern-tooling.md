# Testing with Modern Tooling

## Test layers

| Layer | Purpose |
|---|---|
| unit | domain/application rules without infrastructure |
| integration | EF/database/adapters with real or realistic dependencies |
| functional | HTTP API behavior via test host |
| contract | public API/message compatibility |
| architecture | dependency rules and forbidden references |

## Rules

- Test domain invariants directly.
- Use Testcontainers or real providers for persistence behavior.
- Avoid mocking everything.
- Test authorization and validation for sensitive endpoints.
- Test idempotency and retries for consumers.
- Use deterministic clock/id generation in tests where time/id matters.

## Validation output

Always separate executed tests from suggested tests.
