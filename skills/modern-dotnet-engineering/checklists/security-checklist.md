# Security Checklist

- [ ] No hardcoded real secrets in code, config, tests, Docker, CI, docs, prompts, or examples.
- [ ] Authentication is separate from authorization.
- [ ] Sensitive operations enforce policy/function authorization.
- [ ] Object/entity access enforces resource/tenant ownership (BOLA/IDOR negative cases tested).
- [ ] Property-level read/write authorization and mass-assignment boundaries are explicit.
- [ ] Externally reachable APIs bound payload size, pagination/query complexity, concurrency/rate, and expensive work.
- [ ] Logs/traces mask tokens, cookies, JWTs, connection strings, unnecessary PII, and sensitive prompt/tool content.
- [ ] Raw SQL is parameterized and justified.
- [ ] PII collection, retention, provider exposure, and access are explicit.
- [ ] AI/MCP tool actions, when present, validate schemas and enforce executable authorization; prompt instructions are not trusted as a security control.
