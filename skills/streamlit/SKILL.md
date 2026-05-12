---
name: streamlit
description: use when building, reviewing, auditing target streamlit app quality, debugging, refactoring, testing, packaging, or deploying streamlit apps, dashboards, data tools, ai/ml demos, llm chat interfaces, multipage python apps, streamlit session-state flows, caching, forms, data editors, uploads, downloads, connections, secrets, authentication, docker, community cloud, or production readiness reviews. do not use for generic python scripts, non-streamlit dash or flask apps, frontend-only react work, backend-only apis, or data analysis that does not require streamlit-specific app behavior.
---

# Streamlit

## Mission

Help create, improve, review, debug, test, and deploy Streamlit applications with rerun-aware Python guidance. Optimize for working apps, clear state boundaries, safe secret handling, measurable validation, and maintainable project shape.

Use official Streamlit documentation and official Streamlit repositories as source truth when current API details, deprecations, deployment rules, or license-sensitive claims matter. This package is a clean-room instruction set and must not reuse third-party skill text or scraped documentation blocks.


## Scope

Use this skill only for Streamlit-specific work: application structure, UI behavior, rerun semantics, session state, caching, data connections, charts, chat interfaces, testing, deployment, and security concerns that affect a Streamlit app. Do not take over generic Python, SQL, backend API, React frontend, or non-Streamlit dashboard work unless the Streamlit app boundary is explicit.

## Required input

Resolve or infer these before major implementation or review work:

1. app goal and target users;
2. current app files or desired app structure;
3. Streamlit version when API details are version-sensitive;
4. data source, refresh expectations, file sizes, and privacy constraints;
5. deployment target, authentication model, and secret source when relevant;
6. validation expectation: AppTest, smoke run, manual check, deployment check, or static review.

If these inputs are missing, proceed with explicit assumptions unless the gap affects security, production readiness, version-sensitive APIs, or private data exposure.

## Operating workflow

1. Classify the user request as one or more modes: `new-app`, `feature`, `debug`, `review`, `performance`, `state`, `data`, `ui`, `llm-chat`, `testing`, `deployment`, or `security`.
2. Identify constraints that affect correctness: Streamlit version, data source, deployment target, user count, refresh rate, file size, auth model, secret source, dependency limits, and privacy requirements.
3. Proceed with best-effort implementation or review when the constraints are sufficient. Ask only when a missing detail would make the answer unsafe or likely wrong.
4. For code output, provide runnable Python with minimal dependencies, stable widget keys, explicit state initialization, and validation steps.
5. For reviews, separate confirmed defects, risks, and optional improvements.
6. For security or deployment work, include checks for secrets, uploads, auth, logging, data access, and rollback or smoke validation.

## Progressive loading

Load only the reference needed for the task:

- `references/app-architecture.md`: rerun model, project shape, multipage apps, callbacks, forms, dialogs, fragments, and state boundaries.
- `references/data-caching-connections.md`: cache selection, invalidation, database connections, file handling, refresh, and data freshness.
- `references/ui-interaction.md`: layouts, charts, metrics, dataframes, data editors, uploads, downloads, and UX review.
- `references/llm-chat.md`: chat interfaces, streaming, prompt controls, retrieval, feedback, and LLM safety/cost guardrails.
- `references/testing-validation.md`: AppTest, smoke checks, dependency checks, quality gates, and review report format.
- `references/deployment-security.md`: Community Cloud, Docker, config, secrets, OIDC, uploads, privacy, and production readiness.
- `references/source-hygiene.md`: source hierarchy, attribution, license hygiene, and copy-risk rules.
- `examples/request-patterns.md`: calibration examples for common Streamlit requests.
- `assets/templates/app_skeleton.py`: reusable starting point for a compact data app.
- `assets/templates/review_report.md.template`: reusable structure for app review findings.
- `scripts/validate_streamlit_skill.py`: deterministic structural validator for this package.
- `scripts/package_skill.py`: deterministic package builder that validates before writing `skill.zip`.

## Streamlit design rules

### Rerun model

- Treat the app as a script that reruns after interactions.
- Keep cheap UI rendering in the main flow.
- Move expensive data loading, transforms, model loading, network calls, and client creation behind cached functions.
- Keep durable business data outside session state.
- Store per-user workflow state in `st.session_state` with stable keys.
- Use callbacks only for small state transitions that are easy to reason about.

### Cache choice

- Use `st.cache_data` for serializable outputs such as query results, loaded files, transformed dataframes, API responses, and deterministic inference outputs.
- Use `st.cache_resource` for shared resources such as database engines, model instances, API clients, vector stores, and other singletons.
- Add `ttl`, `max_entries`, clear controls, or manual cache keys when freshness matters.
- Do not cache credentials, raw sensitive uploads, user-specific authorization decisions, or tenant-specific private data unless the isolation model is explicit.

### State and widgets

- Initialize all expected session keys before widgets depend on them.
- Give widgets explicit keys when values need to survive refactors, page moves, or conditional rendering.
- Prefer forms when multiple inputs should be applied together.
- Separate UI state, cached data, and persisted data.
- Avoid storing large dataframes, models, or raw files in session state when a cache or external store is more appropriate.

### App structure

For tiny demos, a single application file is acceptable. For apps with repeated data loading, multiple pages, reusable charts, or testable business rules, recommend a small package layout with separate modules for data access, charts, state helpers, services, and settings. Keep the structure as simple as the current complexity allows.

## Output contract

The required output format depends on the selected mode. Use the contracts below and omit irrelevant empty sections.

## Output format

### New app or feature

Use this shape unless the user asks for only code:

```markdown
## Proposed structure
[files and responsibilities]

## Implementation
[code by file]

## Design rationale
[rerun, state, cache, UX, and dependency reasoning]

## Run and validate
[commands, smoke checks, and expected behavior]

## Risks and assumptions
[version, data, auth, deployment, performance, or privacy assumptions]
```

### Debug or review

```markdown
## Findings
- [severity] [confirmed issue or risk] - [evidence]

## Fix
[smallest safe patch or replacement]

## Validation
[how to reproduce and verify]

## Remaining risk
[only material unresolved concerns]
```

### Deployment or security

```markdown
## Target and assumptions
[deployment platform, auth model, data sensitivity]

## Required configuration
[config, secrets, dependencies, runtime]

## Security checks
[auth, secrets, uploads, data access, logs]

## Validation
[smoke checks, health checks, rollback notes]
```

## Quality gates

Before finalizing substantial guidance, verify:

- The answer accounts for Streamlit reruns.
- Expensive work uses the correct cache decorator or is intentionally uncached.
- User-specific data is not put in shared caches.
- Widget keys and session state are stable where needed.
- Secrets are not hardcoded or printed.
- File upload guidance includes size, type, validation, and privacy considerations when relevant.
- Testing guidance uses AppTest, smoke checks, or clear manual validation.
- Deployment guidance matches the stated platform.
- Version-sensitive APIs are marked for official-doc verification when not already verified.

## Stop conditions

Stop and report the blocker when:

- The user asks to hardcode real credentials or reveal secrets.
- The requested app would expose private data without an access-control model.
- A production-readiness claim is requested without deployment target, auth model, data classification, and validation evidence.
- A precise version-sensitive API answer is required but current documentation cannot be checked and no safe fallback exists.
- The request is not Streamlit-specific and should be handled by ordinary Python, backend, frontend, data-analysis, or deployment guidance.
