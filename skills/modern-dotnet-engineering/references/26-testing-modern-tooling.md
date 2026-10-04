# Testing with Modern .NET Tooling

## Test layers

| Layer | Purpose |
|---|---|
| unit | domain/application rules without infrastructure |
| integration | EF/database/adapters with real or realistic dependencies |
| functional | HTTP API behavior via test host/published service |
| contract | public API/message compatibility |
| architecture | dependency rules and forbidden references |

## Rules

- Test domain invariants directly.
- Use Testcontainers or real provider environments for persistence behavior when container execution is appropriate; do not use mocks/in-memory providers as proof of relational semantics.
- Use functional tests for authentication/authorization, resource ownership, validation, `ProblemDetails`, idempotency, and important API limits.
- Test retry/idempotency/duplicate delivery for consumers and critical side effects.
- Use deterministic time/ID/randomness where those values affect behavior.
- Keep architecture/contract tests for boundaries that agent-assisted changes must not silently break.

## Microsoft.Testing.Platform (MTP)

The .NET 10 SDK can select Microsoft.Testing.Platform natively through global.json:

```json
{
  "test": {
    "runner": "Microsoft.Testing.Platform"
  }
}
```

Adopt MTP when the repository's test frameworks/extensions/CI reporting support it. Treat migration as a tooling contract change, not a blanket rewrite.

### Runner migration checklist

- inventory frameworks/adapters/extensions and their MTP compatibility;
- freeze existing test-discovery count and required result/coverage artifacts;
- update CLI arguments/CI tasks that are runner-specific;
- execute the same representative suites on the selected SDK;
- prove result files, attachments, coverage, filters, and exit semantics still work;
- do not remove VSTest compatibility until the actual CI/IDE matrix is supported.

## Zero/expected-test-count gate

A successful `dotnet test` process is not sufficient if the expected tests were not discovered. For critical pipelines, establish a minimum/expected test count or suite manifest and fail when discovery unexpectedly drops to zero/below the accepted baseline.

## Deterministic time

Prefer `TimeProvider` in application boundaries and `FakeTimeProvider` in tests over sleeping or reading wall-clock time directly. Cross-link time-zone/civil-time rules from `references/30-time-dates-clock-timezone.md`.

## Validation output

Always separate executed tests from suggested tests. Record runner/SDK identity when runner behavior is material.

Fresh source: https://learn.microsoft.com/dotnet/core/testing/migrating-vstest-microsoft-testing-platform
