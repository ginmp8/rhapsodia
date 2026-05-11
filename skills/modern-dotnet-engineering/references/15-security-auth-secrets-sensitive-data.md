# Security: Auth, Secrets, and Sensitive Data

## Required checks

- Authentication verifies identity.
- Authorization verifies permission for the operation and resource.
- Validation rejects malformed input; it does not replace authorization.
- Secrets are never hardcoded or logged.
- PII is minimized, masked, retained intentionally, and access-controlled.

## API security

- Use policy-based authorization for sensitive operations.
- Avoid `AllowAnonymous` except for explicitly public endpoints.
- Use rate limiting for abuse-prone endpoints.
- Protect against mass assignment by using explicit request DTOs.
- Use parameterized SQL or EF/LINQ; never concatenate user input into SQL.

## Secret handling

If a real credential is exposed, recommend: revoke/rotate, remove from active code paths, check logs and CI, assess blast radius, and add automated scanning.
