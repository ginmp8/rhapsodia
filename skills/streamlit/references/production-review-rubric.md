# Production Review Rubric

Use this rubric to evaluate Streamlit apps before sharing them with a wider audience. It is intentionally practical: score only what can be inspected from code, configuration, command output, screenshots, logs, tests, or user-provided evidence. Do not claim production readiness when startup, secrets, critical user flows, or deployment assumptions were not checked.

## Scoring model

Score each dimension from 0 to 5.

- `0`: absent or unsafe.
- `1`: present but fragile or misleading.
- `2`: works in a narrow happy path with major gaps.
- `3`: acceptable for local or limited internal use, with known risk.
- `4`: strong enough for broader internal use after documented validation.
- `5`: robust, tested, observable, and safe for the intended audience.

A release candidate should normally score at least 4 in safety, state, deployment, and validation before broad rollout. A personal prototype can proceed with lower scores when risks are explicitly accepted.

## 1. User workflow clarity

Review whether the app tells users what to do, what each control changes, what result was produced, and what action comes next.

- `0`: the purpose is unclear and outputs lack context.
- `3`: the main path is usable, but empty states, loading states, or next actions are weak.
- `5`: purpose, controls, outputs, empty states, validation messages, and next actions are obvious.

Evidence to inspect: title, page layout, labels, help text, empty-state messages, error messages, form grouping, sidebar organization, and screenshots when available.

## 2. Rerun and state correctness

Review whether Streamlit's top-to-bottom rerun model is handled intentionally.

- `0`: reruns change data, repeat side effects, lose inputs, or corrupt state.
- `3`: common paths work, but conditional widgets, callbacks, or multipage state can drift.
- `5`: session state is initialized once, widget keys are stable, callback order is explicit, and critical flows are tested.

Evidence to inspect: `st.session_state` initialization, widget keys, callbacks, forms, fragments, `st.rerun`, `st.stop`, multipage navigation, and AppTest coverage.

## 3. Side-effect safety

Review writes, external calls, expensive actions, downloads, uploads, and irreversible operations.

- `0`: writes or external actions can repeat accidentally on rerun.
- `3`: writes happen behind buttons, but idempotency, confirmation, or auditability is incomplete.
- `5`: side effects are explicit, authorized, confirmed, idempotent where possible, and auditable.

Evidence to inspect: submit buttons, confirmation flows, database writes, API calls, queue publishing, audit logs, retry behavior, and error recovery.

## 4. Performance and scalability

Review whether the app avoids recomputing expensive work on every interaction and remains usable as data grows.

- `0`: heavy queries, model loads, or transformations run on every rerun.
- `3`: major data loads are cached, but refresh behavior or rendering volume is unclear.
- `5`: data/resource cache boundaries, TTL, invalidation, pagination, sampling, aggregation, and refresh controls are intentional.

Evidence to inspect: `st.cache_data`, `st.cache_resource`, `ttl`, `max_entries`, connection reuse, query limits, data editor size, chart rendering, and memory use assumptions.

## 5. Security, secrets, and privacy

Review whether sensitive values and private data are protected.

- `0`: secrets are hardcoded, uploaded files are trusted blindly, or private data is exposed.
- `3`: secrets are externalized, but authorization, logging, file handling, or download controls need review.
- `5`: secrets, authentication, authorization, uploads, downloads, logging, error handling, and data minimization are covered.

Evidence to inspect: `st.secrets`, `.streamlit/secrets.toml`, environment variables, OAuth/OIDC configuration, file upload validation, logs, exception display, and data export controls.

## 6. Testability

Review whether critical behavior can be checked without clicking manually through every path.

- `0`: no meaningful test or smoke strategy exists.
- `3`: pure functions are testable, but UI and rerun behavior are not covered.
- `5`: pure tests, AppTest scenarios, startup smoke checks, and deployment smoke checks cover critical paths.

Evidence to inspect: pytest tests, `streamlit.testing.v1.AppTest`, fixtures, smoke commands, CI configuration, validation scripts, and manual test notes.

## 7. Deployment readiness

Review whether someone else can run, configure, observe, and recover the app.

- `0`: the app works only on the author's machine.
- `3`: dependencies are listed, but secrets, config, startup, or platform assumptions are incomplete.
- `5`: dependencies, config, secrets, startup command, health/smoke checks, logs, storage, and rollout/rollback notes are documented.

Evidence to inspect: `requirements.txt`, lockfiles, Dockerfile, `.streamlit/config.toml`, `packages.txt`, environment variables, platform settings, logs, and smoke-test output.

## 8. Maintainability

Review whether the app can evolve without fragile edits.

- `0`: one long script mixes UI, state, data access, security, business logic, and side effects.
- `3`: helpers exist, but boundaries or naming are unclear.
- `5`: UI, state, data access, business actions, security checks, and tests have clear boundaries.

Evidence to inspect: module structure, naming, shared utilities, pure functions, dependency direction, comments that explain non-obvious choices, and repeated code.

## Required review output

When producing a review, include these sections and do not leave any section empty:

1. `Verdict`: one of `approve`, `approve with reservations`, or `reject`, followed by the reason.
2. `Scope reviewed`: concrete files, pages, commands, screenshots, or logs inspected.
3. `Top findings`: severity, evidence, impact, and smallest safe fix.
4. `Scorecard`: every dimension scored or marked `not inspected` with a reason.
5. `Required fixes before release`: release blockers only, or `None found from inspected evidence`.
6. `Suggested improvements`: non-blocking improvements, or `None identified from inspected evidence`.
7. `Validation performed`: exact executed checks and outcomes, plus checks not run and why.
8. `Residual risks`: remaining uncertainty and accepted trade-offs.

## Example finding format

| Severity | Evidence | Impact | Smallest safe fix |
|---|---|---|---|
| high | The app entry point calls a write API immediately after a selectbox changes | A rerun can repeat the write without user confirmation | Move the write behind `st.form_submit_button`, add confirmation text, and make the server operation idempotent |
| medium | `load_data()` reads a large CSV without `st.cache_data` | Every widget interaction reloads the file and slows the app | Add `@st.cache_data(ttl="15m")`, expose a refresh button, and document freshness expectations |

## Review gates

Reject or require repair before release when any of these are true:

- startup fails in the target environment;
- secrets, tokens, credentials, or private data are hardcoded or logged;
- side effects can repeat unintentionally on rerun;
- authentication or authorization is required but absent;
- uploads are accepted without file type, size, or parsing controls;
- critical paths cannot be validated by test, smoke check, or manual evidence;
- deployment depends on undocumented local state.

Approve with reservations when issues are non-blocking but should be tracked. Approve only when the inspected evidence supports the intended release scope.
