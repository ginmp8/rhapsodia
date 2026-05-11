# ASP.NET Core 10 API Design

## API design rules

- Design contracts intentionally; do not expose entities.
- Use `ProblemDetails` for errors.
- Use stable route names and explicit status codes.
- Add pagination, filtering, and sorting deliberately.
- Add idempotency keys for critical POST operations.
- Version public contracts before breaking changes.
- Authenticate and authorize by operation, not just by controller/group.

## HTTP semantics

| Outcome | Status |
|---|---|
| created | 201 |
| accepted async processing | 202 |
| validation failure | 400 or 422 by standard/team policy |
| unauthorized | 401 |
| forbidden | 403 |
| not found | 404 |
| conflict/idempotency clash | 409 |

## Boundary rule

API layer adapts HTTP to application commands/queries. It should not own business workflow.
