---
name: frontend-ai-token-efficient
description: use when the user asks for react/typescript frontend architecture, implementation guidance, refactoring, review, scaffolding, checklists, runtime validation, ux/cro tied to code, or frontend leak-prevention so ai agents can modify the project with low context and humans can maintain it safely. covers vite, next.js, react router, feature-based structure, contracts, forms, onboarding, state, api boundaries, design-system usage, tests, accessibility, observability, and browser-side security. do not use for pure backend, native mobile, visual-only design, brand identity, or skill creation.
---

# Frontend AI Token Efficient

## Mission

Help design, review, and guide React/TypeScript frontends that are easy for AI agents to modify with limited context and safe for humans to maintain. Prioritize local structure, explicit contracts, dependency rules, verifiable validation, and leak prevention.

This skill is not a visual-design-first generator. It may review UX, CRO, and visual quality only when they are connected to frontend implementation, existing design-system constraints, accessibility, runtime validation, or maintainable code changes.

## Scope

Use this skill to:

- choose a frontend stack or framework with AI-maintainability as a decision factor;
- propose project structures for React, TypeScript, Vite, Next.js, React Router, or similar stacks;
- review architecture, folders, dependencies, components, forms, state, API access, tests, and repo documentation for AI-assisted maintenance;
- review UX quality when tied to implementation: forms, onboarding, empty states, CTAs, friction, responsiveness, and design-system consistency;
- plan browser or Playwright validation when the task involves real interaction, focus behavior, modals, form errors, responsiveness, or visual regression;
- generate concise guides such as `AI_CONTEXT.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `DEPENDENCY_RULES.md`, `TESTING_GUIDE.md`, `API_GUIDE.md`, `UI_GUIDE.md`, and `SECURITY_FRONTEND.md`;
- review frontend leak risks: secrets, tokens, logs, analytics, storage, URLs, source maps, XSS, CSP, and cache behavior;
- guide implementation or refactoring while keeping the touched file set as small as possible.

Do not use this skill for pure backend work, native mobile, visual-only design without code, skill creation, infrastructure security audits, or repository implementation without a clear frontend scope.

## Core rules

- Reduce required context before reducing lines of code: a change should require reading a small set of feature files and shared contracts.
- Organize by feature and domain; use technical folders only inside a feature or in truly shared layers.
- Prefer small local duplication over premature global abstraction.
- Do not place business rules in `shared`.
- Do not allow direct HTTP calls from components; use an `api/` layer, orchestration hooks, and mappers.
- Never invent an API contract; request it, read it, or mark it as an explicit assumption.
- Never treat the frontend as the security boundary. Real authorization belongs on the backend.
- Never suggest secrets in the bundle, sensitive tokens in web storage, or sensitive payloads in logs or analytics.
- In existing projects, preserve the visual language, UI library, tokens, CSS patterns, and component conventions before suggesting a new aesthetic.
- In a new interface without a design system, define intentional visual direction and explicit tokens; avoid generic generated UI patterns.
- Separate executed validation, recommended validation, and static reasoning.

## Expected inputs

Infer and proceed with explicit assumptions when possible:

1. project type: internal SPA, backoffice, dashboard, public product, content site, or full-stack app;
2. current or intended stack: React, Vite, Next.js, React Router, TanStack, Astro, or similar;
3. target artifact: folder structure, feature, component, diff, PR, guide, checklist, or security policy;
4. constraints: design system, authentication, compliance, sensitive data, team conventions, AI tool, tests, and deployment;
5. expected output: recommendation, plan, checklist, markdown files, review, conceptual patch, or validation commands.

## Modes

Choose one primary mode:

| mode | use when | main output |
|---|---|---|
| `framework-selection` | choosing Vite, Next.js, React Router, TanStack Start, Astro, or supporting stack pieces | decision matrix and recommendation |
| `architecture-plan` | designing structure, dependencies, features, shared layers, entities, and AI docs | architecture proposal and rules |
| `implementation-guidance` | guiding a specific frontend change without editing the repo directly | minimal steps, likely files, validation |
| `code-review` | reviewing a frontend structure, component, hook, feature, diff, or PR | findings by severity and smallest fix |
| `ux-flow-review` | reviewing forms, onboarding, empty states, CTAs, visual accessibility, and friction | UX findings, hypothesis, and smallest adjustment |
| `runtime-validation` | planning or interpreting browser, Playwright, screenshot, log, or real-flow tests | validation plan and expected evidence |
| `security-review` | reviewing frontend leak and browser-side security risk | findings, controls, checklist, and gates |
| `ai-context-docs` | creating or reviewing repository guidance for AI agents | suggested markdown files or ready content |
| `repo-scan` | a local repository is available and a lightweight scan is useful | scanner report plus critical reading |

## Progressive loading

Read only what the task needs:

- `references/framework-selection.md`: framework and stack selection.
- `references/architecture.md`: feature-based structure, duplication, imports, and context documentation.
- `references/implementation-patterns.md`: forms, state, API, mappers, design system, tests, accessibility, performance, and observability.
- `references/ux-quality.md`: project-adapted design, visual quality, form CRO, onboarding, empty states, metrics, and experiments.
- `references/runtime-validation.md`: browser and Playwright validation, visual evidence, logs, runtime accessibility, performance, and specialist agents.
- `references/security.md`: frontend leak prevention and defensive controls.
- `references/review-checklists.md`: architecture, PR, security, and AI-maintainability checklists.
- `references/ai-context-docs.md`: markdown templates for guiding agents.
- `references/output-contracts.md`: response formats for recommendations, reviews, security, and documentation.
- `examples/activation-scenarios.md`: activation and boundary calibration.
- `evals/activation-scenarios.json`: planned scenarios, not executed metrics.
- `scripts/check_frontend_ai_package.py`: optional local scan for common structure and leak signals.

## Workflow

1. Classify the request and choose the mode.
2. State assumptions that affect the answer, especially app type, data sensitivity, and framework.
3. If files, a diff, or a repository are available, inspect them before concluding; do not generalize without evidence.
4. Define the smallest useful context: feature, entity, `shared/api`, `shared/ui`, docs, tests, and, when real UI behavior matters, screenshots or browser validation.
5. In an existing project, inspect visual patterns and components before creating new ones.
6. Apply the reference for the selected mode.
7. Produce the response using the appropriate output contract.
8. Include validation: executed commands, static checks, recommended tests, and unverified risks.

## Optional scanner

When a local repository is available and the user requests a quick audit, run:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format markdown --output <report.md>
```

Use the result as triage only. The scanner does not replace human review: confirm false positives, read relevant files, and explain limitations.

## Output contract

Use `references/output-contracts.md` for specific formats. By default include:

1. assumptions;
2. recommendation or findings;
3. structure, files, or minimal changes;
4. executed and recommended validation;
5. risks, dependencies, and the next highest-value step.

## Stop conditions

Stop, narrow scope, or report a blocker when:

- the change requires a missing API contract and answering would invent a payload;
- the user asks to put a secret, client secret, service token, private key, or password in the frontend;
- the answer depends on internal policy, compliance, or authorization that was not provided;
- the repository or diff is unavailable and the question requires evidence about real files;
- the proposed change would create a global abstraction without a repeated and stable use case;
- the solution would rely on frontend-only security;
- validation, benchmark, or readiness would be claimed without execution or evidence.
