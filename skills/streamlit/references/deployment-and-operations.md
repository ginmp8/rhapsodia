# Deployment and Operations

## Deployment targets

### Streamlit Community Cloud

Best for public or simple apps connected to GitHub. Keep dependencies declared, secrets configured through the platform, and data access appropriate for a hosted environment.

### Self-hosted VM or container

Best for internal apps, private networks, or custom infrastructure. Use Docker, environment-specific config, health checks, logs, and reverse proxy/TLS as needed.

### Kubernetes

Best when platform teams already operate Kubernetes. Package the app as a container, externalize secrets, define resource requests/limits, and add readiness checks.

### Snowflake

Best when the app lives close to Snowflake data and the organization uses Streamlit in Snowflake. Follow Snowflake-specific packaging, permissions, and data-access rules.

## Dependency management

Pin or constrain dependencies enough for reproducibility. Include system packages when needed. Avoid installing from arbitrary URLs unless there is a controlled supply-chain reason.

## Configuration

Keep environment-specific settings out of code. Use config files, environment variables, and secrets. Document required settings in README or deployment notes.

## Observability

At minimum, capture startup logs, user-safe errors, external call failures, and latency around expensive work. For production internal tools, log actor/action/result for writes.

## Deployment checklist

- App starts with declared command.
- Dependencies install from lock/requirements files.
- Secrets are configured in the target platform.
- Upload size limits are intentional.
- Error detail visibility is appropriate.
- Data sources are reachable from the deployment network.
- Caches have acceptable freshness and memory behavior.
- Auth and authorization work in the deployed URL.
- Manual smoke test covers core flow.

## Docker sketch

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

Tune the image for your environment. Do not bake secrets into the image.

## Operational risks

- Memory growth from large cached data.
- Secret misconfiguration.
- Unbounded uploads.
- Slow cold starts from model loading.
- Concurrent users sharing unsafe resources.
- Hidden writes repeated by reruns.
