# Testing and Validation

Use this reference for Streamlit app testing, smoke checks, dependency hygiene, review reports, and validation evidence.

## Testing ladder

1. Static review: imports, page config, state initialization, cache choice, secrets, and deployment files.
2. AppTest checks: render key pages, interact with widgets, verify expected text, tables, or state changes.
3. Smoke run: start the app locally and exercise the critical path manually or through a browser tool.
4. Integration checks: database, auth, file upload, model calls, or external APIs in a safe environment.
5. Deployment smoke: verify startup, secrets, routing, auth callback, and logs on the target platform.

## AppTest guidance

Use AppTest for deterministic UI behavior such as titles, widgets, button clicks, form submissions, and session state transitions. Keep tests focused on user-visible outcomes instead of Streamlit internals.

## Review checklist

Check:

- imports are minimal and available;
- state keys are initialized;
- expensive work is cached intentionally;
- caches do not leak user-specific data;
- widgets have keys when needed;
- exceptions are user-friendly;
- secrets are externalized;
- deployment requirements are documented;
- there is at least one smoke or AppTest path for important flows.

## Validation report fields

For a review or package handoff, report command, status, evidence, and remaining risk. Mark scenario coverage as planned unless prompts were executed and evaluator results were captured.
