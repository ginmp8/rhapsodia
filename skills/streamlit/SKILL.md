---
name: streamlit
description: "build, debug, review, audit, test, deploy, optimize, migrate, and harden streamlit python apps, dashboards, data tools, machine-learning interfaces, chat/llm and agentic apps, multipage apps, custom components, widgets, forms, session state, caching, connections, authentication, secrets, AppTest tests, ASGI integration, deployment, troubleshooting, performance, and production-readiness reviews. use when the user asks for Streamlit code, architecture, UI patterns, state/rerun behavior, testing, components, server integration, deployment, migration, performance, or release readiness. do not use for unrelated web frameworks unless comparing or migrating to/from Streamlit."
---

# Streamlit Skill

## Mission

Build and improve Streamlit applications with production-aware Python patterns. Prefer native Streamlit capabilities, predictable rerun behavior, explicit state management, safe secrets handling, testable code, deployable structure, and evidence-backed claims.

Treat the project's installed/pinned Streamlit version as the compatibility boundary. Use official Streamlit documentation, the Streamlit source repository, and the official agent guidance bundled with the matching Streamlit package as primary external references. Read `references/source-and-license.md` before provenance or license claims.

## Primary workflow

1. Select exactly one primary mode: `build`, `debug`, `review`, `test`, `deploy`, `optimize`, `migrate`, or `reference`.
2. Resolve the exact app/repository target and affected files. When API availability or behavior is version-sensitive, read `references/version-and-source-resolution.md` and use `scripts/resolve_streamlit_context.py` when command execution is available.
3. Read `references/reproducible-workflow.md` for baseline identity, evidence labels, repair order, evaluator protection, final freeze, and truthful claim rules. Treat `references/reproducibility-contract.json` as the machine-readable contract.
4. Load only references needed for the selected branch.
5. Apply the smallest complete change or recommendation that satisfies the request and preserves unrelated behavior.
6. Run or prescribe the narrowest validation that can prove the requested behavior. Prefer repository-owned commands, pytest for pure logic, AppTest for Streamlit behavior, and browser/E2E checks only for browser-owned behavior.
7. After a passing final check, freeze the candidate. Any later edit requires affected validation to rerun.

## Workflow router

- **Version-sensitive API or compatibility**: `references/version-and-source-resolution.md` first; use `references/api-command-guide.md` only as a broad fallback/topic index.
- **Build/architecture**: `references/app-architecture.md`; add layout/data/state/security/deploy references only as needed.
- **Debug state, reruns, fragments, or widgets**: `references/execution-state-and-reruns.md` + `references/widgets-forms-and-callbacks.md`.
- **Dashboards/data tools**: `references/dataframes-charts-and-editors.md` + `references/caching-connections-and-performance.md`.
- **Design/theme/accessibility**: `references/design-accessibility-and-theme.md`.
- **Chat/LLM/agentic UI**: `references/llm-chat-and-rag-apps.md` + security + caching/performance guidance.
- **Auth, authorization, secrets, external systems**: `references/authentication-authorization-and-trust.md` + caching/performance guidance.
- **Custom HTML/JS or components**: `references/custom-components-v2.md`; prefer native elements first.
- **ASGI/FastAPI/Starlette/custom routes/middleware/lifespan**: `references/server-asgi.md`.
- **Test**: `references/testing-and-apptest.md`.
- **Review/release readiness**: `references/production-review-rubric.md` + relevant domain references.
- **Deploy**: `references/deployment-and-operations.md` + `references/troubleshooting.md`.
- **Broader official coverage**: `references/official-concepts-expanded.md` and `references/official-deployment-expanded.md` before claiming a topic is unsupported.

## Scope boundaries

Use this skill for Streamlit Python apps and closely related artifacts: app scripts, pages, Streamlit-specific tests, deployment configs, secrets/config guidance, UI state bugs, caching, data display/editing, LLM/chat interfaces, custom components, ASGI integration, performance, migrations, and production reviews.

Do not use it as the primary workflow for generic FastAPI/React apps, non-Streamlit dashboards, ordinary pandas questions without a Streamlit app, infrastructure-only work, PDFs, spreadsheets, slides, or unrelated repository refactors. For mixed tasks, own the Streamlit surface and keep unrelated implementation within its appropriate workflow.

## Required inputs and assumptions

Infer or request only inputs that materially change correctness:

- primary mode and app type;
- app/repository target and affected files;
- installed/pinned Streamlit and Python versions when compatibility matters;
- data and integrations, including database/API/model clients;
- authentication, authorization, secrets, uploads/downloads, and mutation surfaces;
- deployment target and process model;
- available validation commands/tests and whether execution is possible.

Proceed with explicit assumptions for low-risk guidance. Ask one focused question only when missing information changes API choice, security posture, deployment instructions, or data-mutation behavior.

## Core invariants

- Treat top-to-bottom reruns as the default execution model. Use forms, callbacks, fragments, or supported no-rerun modes deliberately rather than assuming every interaction needs a full rerun.
- Use `st.session_state` for per-session state, not mutable module globals. Treat widget constraints as UX controls, not security boundaries; revalidate security-sensitive values server-side.
- Use `st.cache_data` for reusable computed data and `st.cache_resource` for expensive shared resources. Do not wrap `st.connection` in another resource cache. Bound changing caches with a freshness or size policy.
- Do not cache private user/tenant data under globally shared keys unless isolation is proven by cache arguments and the data contract. Shared mutable resources must be safe for concurrent use.
- Protect side effects. Put writes, submissions, deletes, payments, messages, and external mutations behind explicit actions; design retries/idempotency when supported.
- Prefer native Streamlit elements and theme/config APIs before custom HTML, JavaScript, CSS, or third-party components.
- Prefer `st.navigation` + `st.Page` for new multipage architectures unless project/version constraints justify another pattern.
- Use fragments only when their rerun boundary is understood. Parallel fragments require independent work and thread-safe/shared-state discipline.
- Prefer current APIs for the installed version. Do not introduce deprecated compatibility parameters such as `use_container_width` into new code when the installed version supports `width`.
- Never place real secrets in source files, examples, logs, reports, screenshots, committed config, or generated test fixtures.
- Authentication is not authorization. Protect backend data/actions independently from UI visibility.
- Preserve existing tests, fixtures, acceptance criteria, and security controls unless evidence shows they are wrong and changing them is in scope.
- Separate structural, behavioral, runtime, performance, and perceptual evidence. Never promote unexecuted validation to a pass.

## Default app structure

For non-trivial new apps, start with this shape unless project conventions or the resolved Streamlit version require another architecture:

```python
import streamlit as st

st.set_page_config(page_title="App", layout="wide")

st.session_state.setdefault("initialized", True)

@st.cache_resource
def get_client():
    return None

@st.cache_data(ttl="5m", max_entries=20)
def load_data(params):
    return []

with st.sidebar:
    st.header("Controls")

st.title("App")
```

Keep business logic, data access, side effects, and authorization checks outside rendering code when the app is more than a small prototype.

## Output contract

For `build` or implementation work, provide: approach, smallest useful code/patch, version assumptions, state/rerun implications, security/cache/deployment implications when relevant, and validation evidence or steps.

For `debug`, provide: symptom, likely cause, observed/supplied evidence, minimal fix, and regression check.

For `review`, provide: severity-ranked findings with evidence, impact, smallest safe fix, validation gaps, and residual risk. Do not invent findings for uninspected files.

For `optimize`, provide: baseline method, bottleneck evidence, change, same-method candidate validation, and trade-offs. Do not claim faster/cheaper without comparable measurements.

For `deploy` or `migrate`, provide: source/target assumptions, compatibility/platform risks, smallest required config/code changes, rollback/recovery considerations, and runtime checks.

Label material evidence as `measured`, `observed`, `supplied`, `derived`, `inferred`, `planned`, or `blocked` when ambiguity would otherwise overstate confidence.

## Repair and reproducibility controls

Use `baseline -> smallest causal change -> narrow check -> adjacent checks -> final check`. When objective gates fail, prefer one causal change per round.

For baseline-vs-candidate comparisons, treat pre-change tests, fixtures, scenarios, acceptance criteria, and version/source identity as a frozen evaluator/evidence set. Use the same validation method before and after.

**Freeze after pass:** once final applicable validation passes, the candidate is frozen; later edits invalidate affected evidence. Packaging uses canonical output-alias preflight, deterministic ZIP metadata, atomic delivery with last-good preservation on commit failure, SHA-256 identity, and a durable receipt tied to the packaged bytes.

## Stop conditions

Stop or narrow the answer when:

- credentials, production data, or secrets are required but not provided safely;
- the request asks to bypass authentication, authorization, or secret controls;
- exact version-sensitive API behavior matters and no trustworthy project/install/source evidence is available;
- a deployment/runtime claim requires an unverified platform setting or process model;
- a proposed fix would mutate data on every rerun or make retries non-idempotent without acknowledgement;
- a custom component would execute untrusted JavaScript/HTML without a defensible trust boundary;
- parallel fragments or shared resources would introduce unresolved thread-safety/shared-state risk;
- two consecutive repair rounds fail to reduce the same objective error set;
- passing would require weakening an existing test, fixture, security control, or acceptance criterion without evidence that the evaluator is wrong.

## Bundled resources

- `references/version-and-source-resolution.md`: version evidence hierarchy, local official skill/docs discovery, fallback order, and compatibility claims.
- `references/reproducible-workflow.md`: mode selection, target/version identity, evidence labels, baseline/evaluator protection, repair loop, validation matrix, and final freeze.
- `references/reproducibility-contract.json`: machine-readable modes, evidence labels, hard gates, repair limits, comparison rules, and delivery guarantees.
- `references/source-and-license.md`: provenance, license hygiene, and official source links.
- `references/topic-map.md`: official topic index and quick routing map.
- `references/api-command-guide.md`: broad historical API/topic guide; not authoritative for exact current signatures.
- `references/app-architecture.md`: app architecture, file layout, modularity, multipage strategy.
- `references/execution-state-and-reruns.md`: reruns, session state, callbacks, fragments, dialogs, URL/state binding.
- `references/widgets-forms-and-callbacks.md`: widget design, keys, forms, validation, actions.
- `references/layout-navigation-and-pages.md`: layout, pages, navigation, theming, UX structure.
- `references/design-accessibility-and-theme.md`: native-first visual design, theme configuration, responsive layout, labels, icons, and accessible names.
- `references/dataframes-charts-and-editors.md`: tables, data editor, chart selection, ECharts, geospatial displays, sensitive-data boundaries.
- `references/caching-connections-and-performance.md`: cache boundaries, background refresh, async caching, DB/API/model resources, fragments, performance strategy.
- `references/files-uploads-downloads-and-media.md`: upload/download/media handling and safety.
- `references/llm-chat-and-rag-apps.md`: chat UI, streaming, memory, retrieval, feedback, cost controls.
- `references/auth-secrets-and-security.md`: baseline secrets/security reference retained for compatibility and validator continuity.
- `references/authentication-authorization-and-trust.md`: current OIDC authentication, authorization, client-input trust, private-data, and custom-JS trust guidance.
- `references/custom-components-v2.md`: native-first component decision, Components v2, state/triggers, lifecycle, theming, and JavaScript trust boundaries.
- `references/server-asgi.md`: `st.App`, ASGI composition, routes, middleware, lifespan, FastAPI/Starlette integration.
- `references/testing-and-apptest.md`: pytest/AppTest/browser boundaries, smoke tests, regression scenarios.
- `references/deployment-and-operations.md`: Community Cloud, Docker, Kubernetes, Snowflake, observability.
- `references/official-concepts-expanded.md`: expanded official concept map transformed into implementation guidance.
- `references/official-deployment-expanded.md`: expanded official deployment and operations map transformed into deployment guidance.
- `references/troubleshooting.md`: symptom-oriented debugging guide.
- `references/recipes.md`: reusable patterns and snippets.
- `references/anti-patterns.md`: common failures and safer replacements.
- `references/production-review-rubric.md`: readiness review checklist.
- `scripts/resolve_streamlit_context.py`: dependency-free resolver for installed version, project constraints, local official agent guidance, and CLI location.
- `scripts/validate_modern_streamlit_coverage.py`: independent deterministic gate for the added version-aware references, router links, and regression-scenario inventory.
- `assets/templates/app.py.template`: starter single-page app template.
- `assets/templates/chat-app.py.template`: starter chat/LLM app template.
- `assets/templates/multipage-app.py.template`: function-based multipage app template.
- `assets/templates/apptest-test.py.template`: pytest/AppTest smoke test template.
- `assets/templates/dockerfile.template`: Docker deployment starter.
- `assets/templates/review-report.md.template`: app review report template.
- `examples/review-example.md`: completed production-review example.
- `examples/request-patterns.md`: activation and response calibration examples.
- `evals/activation-scenarios.json`: activation/boundary scenarios.
- `evals/reproducibility-scenarios.json`: core, edge, regression, adversarial, and holdout scenarios.
- `evals/modern-api-scenarios.json`: version-aware modern API/security/testing regression scenarios for future behavioral harnesses.
- `scripts/validate_streamlit_skill.py`: deterministic package validator with machine-readable receipts.
- `scripts/package_skill.py`: deterministic, recovery-aware package builder with SHA-256 receipt.
