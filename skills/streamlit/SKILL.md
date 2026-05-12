---
name: streamlit
description: use when building, reviewing, debugging, refactoring, testing, or deploying streamlit applications, dashboards, data apps, multipage apps, data editors, file upload/download flows, cached queries, session-state workflows, charts, llm chat interfaces, ai/ml demos, authentication, secrets, docker/community-cloud deployments, or production-readiness reviews. do not use for generic python scripts, non-streamlit dash/flask/frontend apps, backend-only apis, pure data analysis, or license-sensitive copying of third-party skill content.
---

# Streamlit

## Mission

Help create, improve, audit, debug, validate, and deploy Streamlit apps with code and guidance that respects Streamlit's rerun model, state semantics, caching behavior, file-upload risks, deployment constraints, and user privacy.

This package is a clean-room Streamlit assistant. It may summarize and point to official Streamlit sources, but it must not reuse copied third-party skill text, scraped documentation blocks, or license-unclear package content.

## Core operating rules

1. Treat every Streamlit app as a rerun-driven script unless the user provides evidence otherwise.
2. Separate UI state, cached data, long-lived resources, persisted data, and secrets.
3. Prefer minimal working code over broad framework scaffolding.
4. Provide stable widget keys when state matters.
5. Use `st.cache_data` for serializable data results and `st.cache_resource` for shared clients, engines, models, and other long-lived resources.
6. Never hardcode real credentials, tokens, private keys, or user secrets in examples.
7. Mark version-sensitive API details for official-doc verification when current docs are unavailable.
8. For production or security claims, require deployment target, auth model, data classification, and validation evidence.
9. Keep generated apps easy to run locally before optimizing for deployment.
10. Do not claim tests, benchmark results, or deployment readiness unless a command was executed or evidence was supplied.

## Request router

Classify the request before answering. Use multiple modes when needed.

| Mode | Use for | Load |
|---|---|---|
| `new-app` | create a Streamlit app from a product/data goal | `references/architecture-and-state.md`, `references/ui-data-visualization.md`, `assets/templates/app_skeleton.py` |
| `feature` | add a widget, chart, form, editor, upload, export, page, or interaction | `references/ui-data-visualization.md`, `references/architecture-and-state.md` |
| `state-debug` | fix rerun loops, disappearing values, callbacks, keys, multipage state, or reset behavior | `references/architecture-and-state.md`, `references/troubleshooting.md` |
| `data-cache` | load data, query databases, refresh results, connect to APIs, tune cache or freshness | `references/data-caching-connections.md` |
| `llm-chat` | build chat UIs, streaming responses, RAG controls, feedback, or AI demo apps | `references/llm-chat-ai.md` |
| `testing` | create AppTest tests, smoke checks, validators, or review gates | `references/testing-validation.md` |
| `deployment` | deploy to Community Cloud, Docker, Kubernetes, private hosting, or configure runtime | `references/deployment-security.md`, `references/production-review-rubric.md` |
| `security-review` | review uploads, secrets, auth, data isolation, logging, or cache privacy | `references/deployment-security.md`, `references/source-hygiene.md` |
| `api-choice` | decide which Streamlit API or pattern to use | `references/api-decision-guide.md`, `references/api-catalog.md` |
| `troubleshooting` | diagnose errors, slow apps, install issues, blank UI, or deployment failures | `references/troubleshooting.md` |
| `recipe` | user asks for a known pattern or example | `references/recipes.md` |
| `license-source` | user asks about copying, attribution, source hygiene, or repository safety | `references/source-hygiene.md` |

## Required inputs

Infer when safe, but explicitly state assumptions for any missing input that affects correctness.

- App purpose and primary users.
- Current file structure or desired project size.
- Streamlit version when APIs, deprecations, or tests are version-sensitive.
- Data source, data sensitivity, update frequency, and expected size.
- Deployment platform, auth model, and secret store when applicable.
- Validation expectation: static review, `streamlit run` smoke test, AppTest, CI, or deployment check.

Ask a follow-up only when proceeding would be unsafe, misleading, or likely to create the wrong architecture. Otherwise make a practical assumption and continue.

## Design checklist for every substantial answer

- Rerun behavior is accounted for.
- Expensive operations are cached or intentionally uncached with rationale.
- Shared cache does not leak user-specific or tenant-specific data.
- `st.session_state` is initialized before use.
- Widgets that influence state have stable explicit keys.
- Forms are used when several inputs should be submitted together.
- File uploads are constrained by type, size, parsing, validation, and privacy rules when relevant.
- Secrets are read from environment variables or `st.secrets`, never inline.
- Charts and tables are chosen for the user's task, not only for visual appeal.
- Deployment guidance matches the stated target.
- Testing guidance has executable or clearly manual checks.

## Output contracts

Use the smallest contract that satisfies the request. Omit empty sections.

### New app or feature

```markdown
## Proposed structure
[files and responsibilities]

## Implementation
[code by file or one complete app]

## Why this works in Streamlit
[rerun, state, cache, widgets, data, UX]

## Run and validate
[commands and expected result]

## Risks and assumptions
[version, data, auth, performance, privacy, deployment]
```

### Debug or review

```markdown
## Findings
1. [severity] [confirmed issue/risk] - [evidence]

## Fix
[smallest safe patch or replacement]

## Validation
[reproduction and verification]

## Remaining risk
[only material unresolved risks]
```

### Deployment or security

```markdown
## Target and assumptions
[platform, runtime, users, data sensitivity]

## Required configuration
[dependencies, config, secrets, env vars, files]

## Security checks
[auth, secrets, uploads, cache isolation, logs, data access]

## Validation and rollback
[smoke checks, monitoring, fallback]
```

### Architecture decision

```markdown
## Recommendation
[recommended pattern]

## Options considered
[option, trade-off, when to use]

## Implementation outline
[minimal sequence]

## Validation
[how to prove the decision works]
```

## Code-generation rules

- Prefer one runnable app.py for small examples.
- For medium apps, use `src/` modules only when they reduce complexity: data.py, state.py, views.py, charts.py, services.py, settings.py.
- Put `st.set_page_config()` near the top of the entrypoint before UI output.
- Use functions for repeated UI sections, but do not over-abstract simple Streamlit code.
- Avoid global mutable state except cached resources that are safe to share.
- Keep dataframes out of `st.session_state` unless small and user-specific.
- Use `pathlib`, typed helper functions, and explicit exception messages for maintainability.
- Include requirements.txt only when deployment or reproducibility is requested.
- Include `.streamlit/config.toml` and `.streamlit/secrets.toml.example` only when configuration/secrets are relevant.

## Review severity

- `blocking`: likely data leak, broken app start, unsafe secret handling, wrong auth boundary, or impossible deployment.
- `high`: severe correctness, performance, state, or data-isolation risk.
- `medium`: likely user-visible bug, maintainability issue, cache staleness, validation gap, or confusing UX.
- `low`: small cleanup or clarity issue.
- `note`: optional improvement with no immediate risk.

## Source and license rules

Use `references/source-hygiene.md` when copying, attribution, license, or third-party package origin matters. For this skill package, prefer original summaries and links over bundled copies of large external docs. Official Streamlit documentation and repositories should be treated as source truth for facts, but do not paste long official-documentation blocks into outputs or this package.

## Stop conditions

Stop and report the blocker when:

- The user asks to expose, print, or hardcode real secrets.
- The requested app would expose private data without an access-control model.
- Production-readiness is requested without deployment target, auth model, data classification, and validation evidence.
- Current version-specific API precision is required but current official docs cannot be checked and no safe fallback exists.
- The task is not Streamlit-specific and should be handled as ordinary Python, backend, frontend, data-analysis, or deployment work.
- The user asks to copy a license-unclear third-party skill or documentation package into a public repo.

## Bundled resources

- `references/reference-map.md`: file map and progressive-loading guidance.
- `references/architecture-and-state.md`: rerun model, session state, callbacks, forms, fragments, dialogs, multipage structure.
- `references/api-decision-guide.md`: API selection guide and common command families.
- `references/api-catalog.md`: broad original catalog of Streamlit feature families and usage rules.
- `references/data-caching-connections.md`: caching, database/API connections, refresh, data privacy, upload/download handling.
- `references/ui-data-visualization.md`: layout, tables, data editor, charts, metrics, UX and accessibility.
- `references/llm-chat-ai.md`: chat interfaces, streaming, RAG, feedback, cost and safety guardrails.
- `references/testing-validation.md`: AppTest, smoke tests, static reviews, deployment gates, review templates.
- `references/deployment-security.md`: config, secrets, auth, Community Cloud, Docker, production checklist.
- `references/production-review-rubric.md`: readiness rubric for production, internal, and public app reviews.
- `references/troubleshooting.md`: common errors and diagnostic flow.
- `references/recipes.md`: reusable app patterns and code sketches.
- `references/source-hygiene.md`: source hierarchy, attribution, and copy-risk rules.
- `examples/request-patterns.md`: calibration examples.
- `evals/activation-scenarios.json`: planned activation and boundary coverage.
- `assets/templates/app_skeleton.py`: clean starter app.
- `assets/templates/review_report.md.template`: review output skeleton.
- `scripts/validate_streamlit_skill.py`: package validator.
- `scripts/package_skill.py`: package builder.
