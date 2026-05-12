# Deployment and Security

## Deployment targets

Common targets:

- Streamlit Community Cloud for public or simple private projects tied to GitHub.
- Docker for controlled runtime and enterprise deployment.
- Kubernetes or platform-as-a-service for scaling and internal network access.
- Snowflake or managed enterprise environments when data and identity live there.
- Internal reverse-proxy setups when authentication and TLS are handled upstream.

Always match guidance to the stated target. If the target is unknown, provide platform-neutral rules and ask only when the details affect safety or correctness.

## Configuration

Use `.streamlit/config.toml` for app/runtime preferences. Use environment variables or `st.secrets` for secrets.

Example local config:

```toml
[server]
headless = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "light"
```

Do not put credentials in `config.toml`.

## Secrets

Acceptable places:

- Streamlit secrets management for Streamlit-hosted apps;
- environment variables injected by the platform;
- cloud secret managers;
- deployment platform secret settings.

Example:

```python
import os
import streamlit as st

api_key = st.secrets.get("API_KEY") or os.environ.get("API_KEY")
if not api_key:
    st.error("Missing API key configuration.")
    st.stop()
```

Do not show raw secret values in UI or logs.

## `.streamlit/secrets.toml.example`

Provide an example file with placeholders, not real values:

```toml
API_KEY = "replace-with-your-api-key"
DATABASE_URL = "postgresql://user:password@host:5432/db"
```

Make sure real `secrets.toml` is ignored by git.

## Authentication

Authentication patterns:

1. Native Streamlit auth APIs when they match the provider and deployment target.
2. Reverse proxy or platform auth where the app receives trusted identity headers.
3. App-level auth for demos only when risks are low and requirements are clear.

Security questions:

- Who can open the app?
- Who can see each dataset/record?
- Is identity verified by a trusted layer?
- Are headers signed or otherwise trusted?
- What happens on logout or expired session?
- Are cached results user/tenant scoped?

## Upload security

File uploads are untrusted input.

Controls:

- restrict extensions/types;
- size limit;
- parse with safe libraries;
- schema validation;
- avoid arbitrary path writes;
- avoid unsafe deserialization;
- avoid storing raw files unless needed;
- delete temporary files;
- scan or reject risky formats for sensitive environments;
- do not feed private uploads to third-party APIs without user/policy approval.

## Database and API security

- Parameterize SQL.
- Use least-privilege database users.
- Prefer read-only credentials for dashboards.
- Do not expose internal IDs unless needed.
- Avoid raw exception messages for untrusted users.
- Use timeouts for network calls.
- Avoid logging sensitive payloads.
- Use per-user authorization checks before data retrieval.

## Docker deployment

Basic Dockerfile shape:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

Add system packages only when required by dependencies. Do not bake secrets into the image.

## Community Cloud checklist

- Public/private GitHub repo access configured.
- requirements.txt present.
- App entrypoint selected.
- Secrets configured in app settings.
- External data/API network access allowed.
- File upload sizes acceptable.
- App does not require local files that are ignored by git.
- Errors checked in logs after deploy.

## Production readiness checklist

Before claiming readiness, require evidence for:

- install and app startup;
- dependency pinning or acceptable version ranges;
- auth and authorization;
- secret management;
- data privacy and cache isolation;
- upload controls;
- error handling and observability;
- deployment smoke test;
- rollback plan;
- owner/on-call or operational responsibility if internal.

## Observability

For internal apps:

- log startup config without secrets;
- log query failures with correlation IDs, not private data;
- show user-friendly errors;
- collect app health and latency if platform supports it;
- display data freshness in the UI;
- keep audit logs for data-changing actions.

## Rollback

Simple rollback options:

- redeploy previous commit;
- pin previous image tag;
- disable write actions via feature flag;
- switch to read-only mode;
- clear bad cache entries;
- restore previous secrets/config.

Include rollback notes when deployment changes are risky.
