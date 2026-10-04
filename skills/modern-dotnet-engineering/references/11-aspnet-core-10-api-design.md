# ASP.NET Core 10 API Design

## API design rules

- Design contracts intentionally; do not expose entities.
- Use `ProblemDetails` consistently for machine-readable errors.
- Use stable route names and explicit status codes.
- Design pagination, filtering, sorting, payload size, upload/export, concurrency, and rate limits deliberately; externally reachable APIs must not have unbounded resource consumption.
- Add idempotency protection for critical retryable POST/state-changing operations where duplicates are harmful.
- Version public contracts before breaking changes when consumers cannot move atomically.
- Authenticate the principal, then authorize the operation and the loaded resource/ownership relationship where access depends on object identity.

## Resource authorization

Group/controller/route authorization proves only a coarse permission boundary. For tenant/entity/user-owned resources, apply resource-based authorization or an equivalent explicit application/domain decision after the resource identity/ownership context is known. Test cross-user and cross-tenant IDs negatively.

## OpenAPI in .NET 10

Built-in ASP.NET Core OpenAPI generation targets OpenAPI 3.1 and JSON Schema 2020-12 semantics. Treat upgrades from older OpenAPI tooling as a contract/tooling migration: custom transformers or downstream generators may need changes.

For public APIs:

- generate the document in CI;
- validate it;
- diff contract changes;
- review removals/renames/type/requiredness/semantic changes before release.

## HTTP semantics

| Outcome | Status |
|---|---|
| created | 201 |
| accepted async processing | 202 |
| validation failure | 400 or 422 by explicit API policy |
| unauthorized | 401 |
| forbidden | 403 |
| not found | 404 |
| conflict/idempotency/concurrency clash | 409 when that contract fits |

## Validation gates

- Functional tests for status codes, `ProblemDetails`, validation, authorization, idempotency, and pagination/resource limits.
- Negative resource-authorization tests: cross-user, cross-tenant, role downgrade, missing claims, and ownership mismatch.
- OpenAPI generation/validation/contract diff for externally consumed contracts.
- Load/abuse tests for rate/resource/timeout policies when production capacity or abuse resistance is claimed.

## Boundary rule

The API layer adapts HTTP to application commands/queries. It should not own business workflow or infer business authorization from routing alone.
