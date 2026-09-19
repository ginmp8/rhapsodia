---
name: streamlit
description: "build, debug, review, audit, test, deploy, optimize, migrate, and harden streamlit python apps, dashboards, data tools, machine-learning interfaces, chat/llm apps, multipage apps, widgets, forms, session state, caching, connections, authentication, secrets, apptest tests, deployment, troubleshooting, performance, and production-readiness reviews. use when the user asks for streamlit code, architecture, ui patterns, state/rerun behavior, testing, deployment, migration, performance, or release readiness. do not use for unrelated web frameworks unless comparing or migrating to/from streamlit."
---

# Streamlit Skill

## Mission

Build and improve Streamlit applications with production-aware Python patterns. Prefer native Streamlit capabilities, predictable rerun behavior, explicit state management, safe secrets handling, testable code, deployable structure, and evidence-backed claims.

Use official Streamlit documentation and the Streamlit source repository as primary external references. Consult `references/source-and-license.md` before making provenance or license claims. Do not copy third-party skill text with unclear licensing.

## Primary workflow

1. Select exactly one primary mode: `build`, `debug`, `review`, `test`, `deploy`, `optimize`, `migrate`, or `reference`.
2. For an existing app, identify the exact target, affected files, Streamlit/Python version evidence when material, and current validation surface.
3. Read `references/reproducible-workflow.md` for baseline, evidence labels, repair order, version policy, final freeze, and truthful claim rules. Treat `references/reproducibility-contract.json` as the machine-readable contract for modes, evidence labels, repair limits, and delivery guarantees.
4. Load only the branch references needed for the selected mode.
5. Apply the smallest complete change or recommendation that satisfies the request.
6. Run or prescribe the narrowest validation that can prove the requested behavior. Prefer repository-owned commands and AppTest when appropriate.
7. After a passing final check, freeze the candidate. Any later edit requires rerunning affected validation.

## Workflow router

- **Build**: `references/app-architecture.md`; add layout/data/state/security/deploy references only as needed.
- **Debug state, rerun, or widgets**: `references/execution-state-and-reruns.md` + `references/widgets-forms-and-callbacks.md`.
- **Dashboards/data tools**: `references/dataframes-charts-and-editors.md` + `references/caching-connections-and-performance.md`; add file/media guidance when uploads or exports exist.
- **Chat/LLM apps**: `references/llm-chat-and-rag-apps.md` + security + caching/performance guidance.
- **Auth, secrets, external systems**: `references/auth-secrets-and-security.md` + `references/caching-connections-and-performance.md`.
- **Test**: `references/testing-and-apptest.md`.
- **Review/release readiness**: `references/production-review-rubric.md` + relevant domain references.
- **Deploy**: `references/deployment-and-operations.md` + `references/troubleshooting.md`.
- **Reference lookup**: `references/api-command-guide.md`; use official docs when exact version-sensitive parameters matter.
- **Broader official coverage**: `references/official-concepts-expanded.md` and `references/official-deployment-expanded.md` before claiming a topic is unsupported.

## Scope boundaries

Use this skill for Streamlit Python apps and closely related artifacts: app scripts, pages, Streamlit-specific tests, deployment configs, secrets/config guidance, UI state bugs, caching, data display, LLM/chat interfaces, performance, migrations, and production reviews.

Do not use it as the primary workflow for generic FastAPI/React apps, non-Streamlit dashboards, ordinary pandas questions without a Streamlit app, infrastructure-only work, PDFs, spreadsheets, slides, or unrelated repository refactors. For mixed tasks, own the Streamlit surface and keep unrelated implementation within its appropriate workflow.

## Required inputs and assumptions

Infer or request only inputs that materially change correctness:

- primary mode and app type;
- app/repository target and affected files;
- Streamlit/Python version or project constraints when API compatibility matters;
- data and integrations, including database/API/model clients;
- authentication, secrets, uploads/downloads, and mutation surfaces;
- deployment target;
- available validation commands/tests and whether execution is possible.

Proceed with explicit assumptions for low-risk guidance. Ask one focused question only when missing information changes API choice, security posture, deployment instructions, or data-mutation behavior.

## Core invariants

- Treat reruns as the central execution model; widget interaction can re-execute the script.
- Use `st.session_state` for per-session state, not mutable module globals.
- Use `st.cache_data` for reusable computed data and `st.cache_resource` for expensive shared resources such as clients, engines, or models.
- Do not cache private user/tenant data under globally shared keys unless isolation is proven by the cache key and data contract.
- Protect side effects. Put writes, submissions, deletes, payments, messages, and external mutations behind explicit actions; design retries/idempotency when the external operation supports it.
- Prefer forms for grouped submission and native Streamlit widgets/layouts before custom HTML/components.
- Use fragments only when their rerun boundary is understood and appropriate for the installed Streamlit version.
- Never place real secrets in source files, examples, logs, reports, screenshots, committed config, or generated test fixtures.
- Authentication is not authorization. Protect backend data/actions independently from UI visibility.
- Preserve existing tests, fixtures, acceptance criteria, and security controls unless evidence shows they are wrong and the user accepts changing them.
- Separate structural, behavioral, runtime, performance, and perceptual evidence. Never promote unexecuted validation to a pass.

## Default app structure

For non-trivial new apps, start with this shape unless project conventions require another architecture:

```python
import streamlit as st

st.set_page_config(page_title="App", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.initialized = True

@st.cache_resource
def get_client():
    return None

@st.cache_data(ttl=300)
def load_data(params):
    return []

with st.sidebar:
    st.header("Controls")

st.title("App")
```

Keep business logic, data access, side effects, and security checks outside rendering code when the app is more than a small prototype.

## Output contract

For `build` or implementation work, provide: approach, smallest useful code/patch, state/rerun implications, security/cache/deployment implications when relevant, and validation evidence or steps.

For `debug`, provide: symptom, likely cause, observed/supplied evidence, minimal fix, and regression check.

For `review`, provide: severity-ranked findings with evidence, impact, smallest safe fix, scorecard or rubric output when requested, validation gaps, and residual risk. Do not invent findings for uninspected files.

For `optimize`, provide: baseline method, bottleneck evidence, change, same-method candidate validation, and trade-offs. Do not claim faster/cheaper without comparable measurements.

For `deploy` or `migrate`, provide: source/target assumptions, compatibility or platform risks, smallest required config/code changes, rollback/recovery considerations, and runtime checks.

Label material evidence as `measured`, `observed`, `supplied`, `derived`, `inferred`, `planned`, or `blocked` when ambiguity would otherwise overstate confidence.

## Repair loop

Use `baseline -> smallest causal change -> narrow check -> adjacent checks -> final check`. When objective gates fail, prefer one causal change per round.

## Reproducibility controls

For baseline-vs-candidate comparisons, treat the pre-change tests, fixtures, scenarios, and acceptance criteria as a **frozen evaluator**. Freeze evaluator inputs before candidate mutation when a trustworthy improvement comparison is required. Use the same validation method before and after.

**Freeze after pass:** once final applicable validation passes, the candidate is frozen; later edits invalidate affected evidence. Keep structural evidence, behavioral evidence, runtime evidence, performance evidence, and perceptual evidence separate.

Packaging uses **canonical output alias preflight**, deterministic ZIP metadata, **atomic delivery** with last-good preservation on commit failure, SHA-256 identity, and a complete **durable receipt** tied to the packaged bytes.

## Stop conditions

Stop or narrow the answer when:

- credentials, production data, or secrets are required but not provided safely;
- the request asks to bypass authentication, authorization, or secret controls;
- exact version-sensitive API behavior matters and no trustworthy version/source evidence is available;
- a deployment claim requires an unverified platform setting;
- a proposed fix would mutate data on every rerun or make retries non-idempotent without acknowledgement;
- two consecutive repair rounds fail to reduce the same objective error set;
- passing would require weakening an existing test, fixture, security control, or acceptance criterion without evidence that the evaluator is wrong.

## Bundled resources

- `references/reproducible-workflow.md`: mode selection, target/version identity, evidence labels, baseline/evaluator protection, repair loop, validation matrix, and final freeze.
- `references/reproducibility-contract.json`: machine-readable modes, evidence labels, hard gates, repair limits, comparison rules, and delivery guarantees.
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
- `assets/templates/dockerfile.template`: Docker deployment starter.
- `assets/templates/review-report.md.template`: app review report template.
- `examples/review-example.md`: completed production-review example.
- `examples/request-patterns.md`: activation and response calibration examples.
- `evals/activation-scenarios.json`: activation/boundary scenarios.
- `evals/reproducibility-scenarios.json`: core, edge, regression, adversarial, and holdout scenarios for future behavioral harnesses.
- `scripts/validate_streamlit_skill.py`: deterministic package validator with machine-readable receipts.
- `scripts/package_skill.py`: deterministic, recovery-aware package builder with SHA-256 receipt.
