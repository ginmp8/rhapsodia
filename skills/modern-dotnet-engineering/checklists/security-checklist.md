# Security Checklist

- [ ] No hardcoded real secrets in code, config, tests, Docker, CI, or docs.
- [ ] Authorization is policy/resource based for sensitive operations.
- [ ] Logs mask tokens, cookies, JWTs, connection strings, and unnecessary PII.
- [ ] Public request DTOs prevent mass assignment.
- [ ] Raw SQL is parameterized and justified.
- [ ] PII collection, retention, and access are explicit.
