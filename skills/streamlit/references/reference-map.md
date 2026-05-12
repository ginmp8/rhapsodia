# Reference Map

Use this file to decide which reference to load. Do not load every reference by default.

## Loading policy

1. Read `SKILL.md` first.
2. Load the smallest reference that matches the user's active problem.
3. Prefer recipes only when the user asks for an example or pattern.
4. Prefer troubleshooting only after an error, symptom, failed deployment, or confusing runtime behavior.
5. Prefer source hygiene only for license/copying/attribution concerns.
6. If multiple references apply, read in this order: architecture/state, data/cache, UI, security/deployment, testing.

## Resource roles

| File | Role | Typical trigger |
|---|---|---|
| `references/architecture-and-state.md` | Explains Streamlit execution, state, forms, callbacks, fragments, dialogs, pages, and project shape. | Rerun bug, state workflow, multipage app, complex interaction. |
| `references/api-decision-guide.md` | Helps choose Streamlit commands and avoid API misuse. | "Which API should I use?", command selection, widgets/charts/table choice. |
| `references/api-catalog.md` | Broader catalog of Streamlit API families and usage guidance. | User asks for API coverage, supported feature families, or command alternatives. |
| `references/data-caching-connections.md` | Guides data loading, cache, connections, uploads, downloads, and freshness. | Database, CSV upload, query cache, performance, tenant data. |
| `references/ui-data-visualization.md` | Guides layout, tables, charts, metrics, filter UX, and accessibility. | Dashboard, chart, layout, editor, filter panel. |
| `references/llm-chat-ai.md` | Guides chat apps, streaming, RAG, feedback, memory, cost, and safety. | LLM chatbot, AI assistant UI, streaming response. |
| `references/testing-validation.md` | Provides validation strategy and examples. | Tests, AppTest, CI, review, smoke validation. |
| `references/deployment-security.md` | Guides secrets, auth, config, deploy targets, Docker, production readiness. | Community Cloud, Docker, OIDC, secrets, public app. |
| `references/production-review-rubric.md` | Readiness rubric for production reviews. | User asks if an app is production-ready or safe to publish. |
| `references/troubleshooting.md` | Diagnostic decision tree. | Error, slow app, blank app, weird rerun, deploy failure. |
| `references/recipes.md` | Reusable patterns. | User asks for a complete example or template. |
| `references/source-hygiene.md` | Licensing, clean-room rewriting, attribution. | Copying from another repo or publishing under a license. |

## Output expectations

A good Streamlit answer usually includes:

- the smallest runnable code or patch;
- why the code survives reruns;
- cache/state boundaries;
- exact run command;
- validation steps;
- risks and assumptions.

Avoid long conceptual explanations when a focused code change is enough. Add a deeper explanation only when the user is designing architecture, reviewing production readiness, or debugging a subtle rerun/state problem.
