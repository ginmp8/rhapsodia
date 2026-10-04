# Security: Authentication, Authorization, Secrets, and Sensitive Data

## Required checks

- Authentication verifies identity.
- Authorization verifies permission for the operation and the specific resource/object when access depends on ownership, tenant, or object properties.
- Validation rejects malformed input; it does not replace authorization.
- Secrets are never hardcoded or logged.
- PII is minimized, masked, retained intentionally, and access-controlled.

## API authorization risks

Review explicitly for OWASP API authorization failures:

- broken object-level authorization (BOLA/IDOR): accepting an object ID and loading it without checking actor/tenant ownership;
- broken object-property-level authorization: exposing or accepting properties the actor must not read/write;
- function-level authorization: an authenticated actor reaches an operation outside their role/capability;
- sensitive business-flow abuse: valid endpoints used at abusive scale/order/frequency.

Use policy/resource-based authorization or equivalent explicit application/domain rules. Gateway/route policies can provide coarse control but must not be the only object-level boundary.

## Resource-consumption security

Externally reachable APIs need bounded:

- payload/upload/export size;
- pagination/page size and filter/query complexity;
- request concurrency and rate;
- timeouts and expensive downstream work;
- queue/backlog admission.

Unbounded resource consumption is a correctness, availability, and cost risk even when authentication is correct.

## API security

- Avoid `AllowAnonymous` except for explicitly public endpoints.
- Protect against mass assignment with explicit request DTOs/mapping.
- Use parameterized SQL or EF/LINQ; never concatenate user input into SQL.
- Test cross-user/cross-tenant access and property-level update/read restrictions.

## Secret handling

If a real credential is exposed, recommend: revoke/rotate, remove from active code paths, check logs/CI/artifacts, assess blast radius, and add automated scanning/prevention.
