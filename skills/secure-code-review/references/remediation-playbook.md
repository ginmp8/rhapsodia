# Secret Handling Remediation Playbook

## Immediate containment

- Revoke or rotate exposed credentials first.
- Do not rely on “we removed it from the latest commit” as the only response.
- Check whether the value also appears in build logs, screenshots, tickets, PR discussions, or copied examples.

## Safe replacement patterns

### Better than hardcoding

1. workload identity or instance role
2. managed secret store
3. deployment-injected environment variables

### Code replacement guidance

- Replace literals with configuration lookups.
- Keep secret names stable and descriptive.
- Fail closed when a required secret is absent.
- Avoid fallback defaults for secrets.

Example pattern:

```text
BAD: api_key = "real-secret-value"
BETTER: api_key = getenv("SERVICE_API_KEY")
BEST: fetch short-lived credential via platform identity
```

## Logging guidance

- Never log authorization headers, cookies, JWTs, API keys, or full connection strings.
- Prefer structured logs with field-level redaction.
- Mask all but a minimal suffix when an identifier must be referenced operationally.

## Repository hygiene

- Keep `.env` untracked.
- Keep `.env.example` free of real values.
- Add or verify ignore rules for local secret files.
- Enable automated secret scanning and, where available, push protection.

## Review checklist

- remove the literal from code and config
- rotate or revoke the credential
- verify there are no copies in logs or docs
- verify least privilege
- add preventive controls
