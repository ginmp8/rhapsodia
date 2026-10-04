# Server and ASGI Integration

## Use only for real server-composition requirements

A normal Streamlit app should remain a normal Streamlit script. Introduce `st.App`/ASGI composition only when the resolved Streamlit version supports it and the app genuinely needs custom routes, middleware, lifespan hooks, programmatic server composition, or mounting with another ASGI framework.

## Supported use cases

- custom health/webhook/API routes beside the UI;
- HTTP middleware such as security headers or request logging;
- process-level startup/shutdown work;
- mounting FastAPI/Starlette beside or around Streamlit;
- process-level shared state/resources that are not per-user session state.

Do not use ASGI composition merely to set a port, theme, headless mode, or ordinary Streamlit config.

## Boundaries

Keep UI code in the Streamlit script and server composition in a launcher/module. Treat ASGI lifespan state as process-level, not per-session. Route/middleware authentication still needs resource-level authorization.

## Lifespan and cached resources

Warm shared cached resources only after the Streamlit runtime is available. For scheduled/background refresh, define freshness/staleness semantics explicitly and avoid blocking the ASGI event loop with synchronous work. Multi-worker deployments initialize/warm each process independently.

## FastAPI/Starlette integration

When one framework owns the parent ASGI app, preserve correct lifespan/startup semantics for the mounted Streamlit app. Namespace custom routes and avoid conflicts with Streamlit-reserved/internal routes.

## Validation

Static imports do not prove ASGI composition works. Run process startup, route, middleware, shutdown, and deployment smoke checks appropriate to the actual server topology.
