---
name: streamlit
description: "build, debug, review, audit, test, deploy, and harden streamlit python apps, dashboards, data tools, machine-learning interfaces, chat/llm apps, multipage apps, widgets, forms, session state, caching, connections, authentication, secrets, apptest tests, deployment, troubleshooting, and production-readiness reviews. use when the user asks for streamlit code, architecture, ui patterns, performance, state/rerun behavior, app testing, deployment, or migration guidance. do not use for unrelated web frameworks unless comparing or migrating to/from streamlit."
---

# Streamlit Skill

## Mission

Help build and improve Streamlit applications with production-aware Python patterns. Prefer native Streamlit capabilities, predictable rerun behavior, explicit state management, safe secrets handling, testable code, and deployable app structure.

This skill is a practical engineering guide, not a verbatim copy of any external skill package. It uses official Streamlit documentation as source material and references it by URL, while providing original operational guidance for ChatGPT-assisted development.

## Source and license policy

Before making license or provenance claims, consult `references/source-and-license.md`. Treat Streamlit official docs and source repository as Apache-2.0 source references. Do not copy text from third-party skill packages with unclear license. When adding new content, synthesize and rewrite from official sources, current code, and user requirements.

## Workflow router

1. **Creating a new app**: use `references/app-architecture.md`, then pick UI/data/state/deploy references as needed. Start with a minimal app skeleton and expand only after the workflow is clear.
2. **Fixing rerun, state, or widget behavior**: use `references/execution-state-and-reruns.md` and `references/widgets-forms-and-callbacks.md`.
3. **Building dashboards or data tools**: use `references/dataframes-charts-and-editors.md`, `references/caching-connections-and-performance.md`, and `references/files-uploads-downloads-and-media.md`.
4. **Building chat or LLM apps**: use `references/llm-chat-and-rag-apps.md` plus the security and performance references.
5. **Adding authentication, secrets, or external systems**: use `references/auth-secrets-and-security.md` and `references/caching-connections-and-performance.md`.
6. **Testing or reviewing quality**: use `references/testing-and-apptest.md` and `references/production-review-rubric.md`.
7. **Deployment and operations**: use `references/deployment-and-operations.md` and `references/troubleshooting.md`.
8. **Looking up a command**: use `references/api-command-guide.md` first, then open official docs URLs listed there when exact parameters matter.
9. **Needing broader official coverage**: use `references/official-concepts-expanded.md` for expanded concept coverage and `references/official-deployment-expanded.md` for expanded deployment coverage before claiming a topic is unsupported.

## Scope boundaries

Use this skill for Streamlit Python apps and closely related artifacts: app scripts, pages, Streamlit-specific tests, deployment configs, secrets/config guidance, UI state bugs, caching, data display, LLM/chat Streamlit interfaces, and production reviews. Do not use it as the primary workflow for generic FastAPI/React apps, non-Streamlit dashboards, ordinary pandas questions without a Streamlit app, infrastructure-only work, PDFs, spreadsheets, slides, or unrelated repository refactors. When a task is only partly Streamlit-related, handle the Streamlit app surface and hand off unrelated implementation details to the appropriate skill or general coding workflow.

## Required inputs

Before producing Streamlit code, reviews, or deployment guidance, infer or request only the details that materially affect correctness:

- target task: create, debug, review, test, deploy, migrate, or optimize;
- app context: single page, multipage, dashboard, data editor, chat/LLM app, internal tool, or public app;
- runtime and source: local files, pasted code, repository paths, screenshots, logs, or error messages;
- data and integrations: files, database/API connections, model clients, uploads, downloads, authentication, and secrets;
- validation expectation: pytest, `streamlit.testing.v1.AppTest`, startup smoke test, deployment smoke test, or manual review;
- deployment target: local, Community Cloud, Docker, Kubernetes, Snowflake, or another hosted environment;
- safety constraints: no real secrets in examples, no unsafe writes on rerun, no unverified production-readiness claims.

If these inputs are incomplete, proceed with explicit assumptions for low-risk guidance. Ask a focused question only when a missing detail changes API choice, security posture, deployment instructions, or data-mutation behavior.

## Core principles

- Treat reruns as the central execution model. Every widget interaction can re-execute the script.
- Use `st.session_state` for per-session state, not global variables.
- Use `st.cache_data` for reusable computed data and `st.cache_resource` for shared expensive resources such as clients, engines, or models.
- Protect side effects. Put writes, submissions, deletes, and external mutations behind explicit buttons, forms, or confirmation dialogs.
- Prefer forms for grouped input, fragments for isolated expensive refresh areas, and multipage navigation only when one page becomes conceptually overloaded.
- Prefer native Streamlit widgets/layouts before custom HTML or components.
- Never place real secrets in source files, examples, logs, generated reports, or committed config.
- Separate executed validation from suggested validation. Do not claim tests, packaging, deployment, or benchmark results passed unless commands were run or results were supplied.

## Default app structure

For non-trivial apps, produce code in this shape unless the user requests a different architecture:

```python
import streamlit as st

st.set_page_config(page_title="App", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.initialized = True

@st.cache_resource
def get_client():
    # Create a database/API/model client here.
    return None

@st.cache_data(ttl=300)
def load_data(params):
    # Load and transform data here.
    return []

with st.sidebar:
    st.header("Controls")
    # Collect filters or navigation choices.

st.title("App")
# Render metrics, charts, tables, and actions.
```

## Response style

When helping with Streamlit, include:

1. The recommended approach.
2. The smallest useful code or patch.
3. State/rerun implications.
4. Caching, security, or deployment considerations when relevant.
5. Validation steps: AppTest, smoke command, or manual checks.

For reviews, use severity-ranked findings and identify the smallest safe fix. For troubleshooting, start with the symptom, likely cause, evidence to collect, and minimal repair.

## Output contract

For implementation help, provide: approach, code or patch, state/rerun notes, cache/security/deployment notes when relevant, and validation steps. For debugging, provide: symptom, likely cause, evidence to collect, minimal fix, and regression check. For reviews, provide: severity-ranked findings, evidence, impact, smallest fix, and validation gaps. For production readiness, provide: verdict, scorecard, blocking risks, recommended fixes, and executed versus suggested validation.

## Stop conditions

Stop or narrow the answer when:

- the requested behavior requires credentials, production data, or secrets that are not provided safely;
- the user asks to bypass authentication, leak secrets, or disable security controls;
- exact current API details matter and no official source is available in the environment;
- a deployment claim would require a platform-specific setting that has not been verified;
- a proposed fix would mutate data on every rerun or create unsafe side effects.

## Bundled resources

- `references/source-and-license.md`: provenance, license hygiene, and official source links.
- `references/topic-map.md`: official topic index and quick routing map.
- `references/api-command-guide.md`: broad API command guide with use cases, pitfalls, and official links.
- `references/app-architecture.md`: app architecture, file layout, modularity, multipage strategy.
- `references/execution-state-and-reruns.md`: reruns, session state, callbacks, fragments, dialogs.
- `references/widgets-forms-and-callbacks.md`: widget design, keys, forms, validation, actions.
- `references/layout-navigation-and-pages.md`: layout, pages, navigation, theming, UX structure.
- `references/dataframes-charts-and-editors.md`: tables, data editor, chart selection, geospatial displays.
- `references/caching-connections-and-performance.md`: cache boundaries, DB/API/model resources, performance strategy.
- `references/files-uploads-downloads-and-media.md`: upload/download/media handling and safety.
- `references/llm-chat-and-rag-apps.md`: chat UI, streaming, memory, retrieval, feedback, cost controls.
- `references/auth-secrets-and-security.md`: secrets, OIDC auth, permissions, safe deployment defaults.
- `references/testing-and-apptest.md`: AppTest, smoke tests, unit boundaries, regression scenarios.
- `references/deployment-and-operations.md`: Community Cloud, Docker, Kubernetes, Snowflake, observability.
- `references/official-concepts-expanded.md`: expanded official concept map transformed into implementation guidance.
- `references/official-deployment-expanded.md`: expanded official deployment and operations map transformed into deployment guidance.
- `references/troubleshooting.md`: symptom-oriented debugging guide.
- `references/recipes.md`: reusable patterns and snippets.
- `references/anti-patterns.md`: common failures and safer replacements.
- `references/production-review-rubric.md`: readiness review checklist.
- `assets/templates/app.py.template`: starter single-page app template.
- `assets/templates/chat-app.py.template`: starter chat/LLM app template.
- `assets/templates/multipage-app.py.template`: function-based multipage app template.
- `assets/templates/apptest-test.py.template`: pytest/AppTest smoke test template.
- `assets/templates/dockerfile.template`: Docker deployment starter for Streamlit apps.
- `assets/templates/review-report.md.template`: app review report template.
- `examples/review-example.md`: completed example of a production review using the rubric.
- `examples/request-patterns.md`: activation and response calibration examples.
- `evals/activation-scenarios.json`: planned activation and non-activation cases.
- `scripts/validate_streamlit_skill.py`: structural validator for this package.
- `scripts/package_skill.py`: deterministic package builder.
