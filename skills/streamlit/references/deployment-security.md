# Deployment and Security

Use this reference for deployment planning, Streamlit Community Cloud, Docker, configuration, secrets, auth, uploads, privacy, logs, and production readiness.

## Configuration

Keep app configuration separate from secrets. Use project-level Streamlit config for layout, upload limits, server behavior, and theme. Use environment variables or Streamlit secrets for credentials and tokens.

## Secrets

Never hardcode real secrets. Do not print secrets in the UI or logs. Use placeholder names in examples and make it clear where the value should be configured.

## Authentication

When using authentication, define:

- identity provider;
- callback or redirect settings;
- who can access the app;
- how user identity maps to data authorization;
- logout behavior;
- failure behavior when auth metadata is missing.

## Upload security

For file uploads:

- restrict type and size;
- validate structure before processing;
- avoid executing uploaded content;
- avoid storing uploads unless required;
- document retention and access for uploaded data.

## Docker and platform deployment

For Docker, use a slim Python image, install only required packages, expose the Streamlit port, and configure a health check when the platform supports it. For hosted platforms, verify dependencies, secrets, startup command, memory limits, and logs.

## Production readiness

Do not claim production readiness without evidence for startup, auth, data access, secrets, observability, backup or rollback, error handling, and load expectations.
