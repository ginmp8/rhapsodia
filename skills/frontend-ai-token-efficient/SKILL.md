---
name: frontend-ai-token-efficient
description: use when the user asks for react/typescript frontend architecture, implementation guidance, refactoring, review, scaffolding, checklists, runtime validation, ux/cro tied to code, or frontend leak-prevention so ai agents can modify the project with low context and humans can maintain it safely. covers vite, next.js, react router, feature-based structure, contracts, forms, onboarding, state, api boundaries, design-system usage, tests, accessibility, observability, and browser-side security. do not use for pure backend, native mobile, visual-only design, brand identity, or skill creation.
---

# Frontend AI Token Efficient

## Mission

Help design, review, and guide React/TypeScript frontends that are easy for AI agents to modify with limited context and safe for humans to maintain. Optimize for **small sufficient context**, explicit ownership/contracts, bounded scope, evidence-backed findings, and verifiable validation rather than for fewer lines of code alone.

This is not a visual-design-first generator. UX, CRO, and visual quality belong here only when tied to frontend implementation, an existing design system, accessibility, runtime behavior, or maintainable code changes.

## Scope

Use this skill to:

- choose a frontend stack with AI-maintainability as a decision factor;
- design or review React/TypeScript, Vite, Next.js, React Router, TanStack, Astro, or similar frontend structure;
- review folders, dependencies, components, forms, state, API access, tests, accessibility, observability, and AI-facing repo docs;
- review UX implementation for forms, onboarding, empty states, CTAs, responsiveness, friction, and design-system consistency;
- plan or interpret browser/Playwright validation;
- create concise `AI_CONTEXT.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `DEPENDENCY_RULES.md`, `TESTING_GUIDE.md`, `API_GUIDE.md`, `UI_GUIDE.md`, `SECURITY_FRONTEND.md`, and related guidance when useful;
- review browser-side leak risks: secrets, tokens, storage, logs, analytics, URLs, source maps, XSS, CSP, cache behavior, and frontend authorization assumptions;
- guide focused implementation/refactoring while minimizing touched files and context expansion.

Do not use for pure backend work, native mobile, visual-only design without frontend implementation, brand identity, skill creation, infrastructure security audits, or repository implementation without a clear frontend scope.

## Invariants

- Reduce required context before reducing code size.
- Existing project conventions win unless evidence shows a correctness, security, coupling, accessibility, or context-cost problem.
- Prefer feature/domain ownership; keep business rules out of generic `shared` layers.
- Prefer small local duplication over premature global abstraction.
- Components do not call transport clients directly; use feature/API boundaries, orchestration hooks, schemas, and mappers.
- Never invent an API contract. Read it, request it, or mark it as missing/assumed.
- Frontend authorization is UX only; backend authorization is the security boundary.
- Never put secrets in browser bundles, sensitive session material in web storage by default, or sensitive payloads in logs/analytics/URLs.
- Preserve the existing visual language, UI library, design tokens, CSS conventions, and component patterns before introducing new aesthetics.
- Separate evidence from recommendation. Never turn static reasoning into an executed validation claim.
- Do not expand repository scope merely to feel comprehensive.

## Expected inputs

Infer only when low-risk and state material assumptions:

1. app type: internal SPA, backoffice, dashboard, public product, content site, or full-stack app;
2. stack and relevant versions;
3. target artifact: structure, feature, component, diff, PR, docs, checklist, security policy, or runtime flow;
4. constraints: design system, API contracts, authentication, sensitive data, compliance, team conventions, tests, deployment, and AI tooling;
5. desired output: recommendation, plan, review, patch guidance, markdown files, scanner report, or validation plan.

## Modes and deterministic routing

Choose exactly one **primary mode**. Supporting concerns may load extra references, but the primary mode owns the response contract.

| mode | use when | main output |
|---|---|---|
| `framework-selection` | choosing framework or major frontend stack pieces | decision matrix + conditions that would change the choice |
| `architecture-plan` | structure, boundaries, dependencies, feature ownership, migration | target architecture + minimal migration sequence |
| `implementation-guidance` | a specific change without directly editing the repo | smallest implementation plan + likely files + validation |
| `code-review` | diff, PR, component, hook, feature, or repository code review | evidence-backed findings by severity + smallest fixes |
| `ux-flow-review` | implementation-linked forms, onboarding, empty states, CTAs, friction | findings + hypothesis/metric + smallest adjustment |
| `runtime-validation` | browser, Playwright, screenshots, traces, logs, interaction behavior | validation plan or interpreted runtime evidence |
| `security-review` | browser leak/security posture or frontend trust-boundary review | security findings + required controls + validation |
| `ai-context-docs` | create/review agent-facing repo guidance | minimal files/content tied to actual repo decisions |
| `repo-scan` | user explicitly wants a lightweight local scanner pass | machine-readable scanner triage + critical reading |

Routing precedence when multiple intents overlap:

1. an explicit in-scope user request for a mode wins;
2. browser security/leak risk -> `security-review`;
3. requested execution/interpretation of browser behavior -> `runtime-validation`;
4. diff/PR/code defect review -> `code-review`;
5. structure/dependency/ownership decision -> `architecture-plan`;
6. concrete change plan -> `implementation-guidance`;
7. UX/friction question tied to code -> `ux-flow-review`;
8. repository guidance docs -> `ai-context-docs`;
9. framework/stack choice -> `framework-selection`;
10. `repo-scan` is supplemental unless the user explicitly asks for a scan.

If two modes remain equally primary and would materially change the answer, ask one precise question. Otherwise choose the higher-precedence mode and declare the secondary concern.

## Progressive loading

Read only what the selected mode requires:

- `references/framework-selection.md`: framework and stack selection.
- `references/architecture.md`: feature structure, dependency direction, duplication, state ownership, and context locality.
- `references/implementation-patterns.md`: forms, state, API, mappers, design system, testing, accessibility, performance, and observability.
- `references/ux-quality.md`: implementation-linked UX/CRO, onboarding, forms, visual quality, metrics, and experiments.
- `references/runtime-validation.md`: browser/Playwright evidence, accessibility, performance, logs, screenshots, and traces.
- `references/security.md`: frontend leak prevention and browser-side defensive controls.
- `references/review-checklists.md`: architecture, PR, security, UX, runtime, AI-maintainability, and reproducibility checks.
- `references/ai-context-docs.md`: concise repo-documentation templates.
- `references/output-contracts.md`: stable response/finding/evidence schemas.
- `references/reproducibility.md`: context budgeting, evidence labels, repair loop, comparison, and final freeze.
- `examples/activation-scenarios.md`: activation and boundary examples.
- `evals/activation-scenarios.json`: planned activation scenarios; never report metrics without execution.
- `evals/reproducibility-scenarios.json`: planned behavior/regression scenarios; not measured evidence by itself.
- `scripts/check_frontend_ai_package.py`: optional deterministic local scanner for common structure and leak signals.

## Context-budget protocol

For repository work, minimize context deliberately:

1. start with the user-specified files/diff plus repository instructions relevant to those paths;
2. add direct contracts needed to understand them: imported types/schemas, API boundary, feature README, nearest tests, and design-system primitive when materially involved;
3. expand only for a concrete trigger: unresolved dependency, contract ownership, cross-feature interaction, shared abstraction ownership, security boundary, route/config behavior, or a failing runtime/test signal;
4. record important inspected surfaces and material uninspected dependencies in the answer;
5. do not infer repository-wide architecture from top-level folders or a scanner report alone.

A whole-repository read is not the default. Search/navigate first, then read the smallest sufficient set.

## Workflow

1. Establish target identity, scope, and requested outcome.
2. Select one primary mode using the routing rules.
3. Identify evidence already available versus assumptions/missing contracts.
4. Build the smallest sufficient context set using the context-budget protocol.
5. Apply only the references needed for the primary mode and material secondary concerns.
6. Produce the smallest coherent recommendation, finding set, or change plan. Prefer causal fixes over broad cleanup.
7. Validate at the lowest reliable layer available: parse/type/lint/test -> focused runtime/browser checks -> perceptual/manual review when applicable.
8. If a gate fails, repair the diagnosed cause, rerun the same gate, then adjacent gates. Stop a repair branch after two consecutive non-improving rounds unless new evidence changes the diagnosis.
9. Label evidence using `references/reproducibility.md` and `references/output-contracts.md`.
10. **Freeze after pass:** once the final evidence-backed result is established, treat it as frozen. Any later material edit invalidates the affected validation and requires rerun.

## Optional scanner

For an explicitly requested lightweight local audit:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format json
```

or:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format markdown --output <report.md>
```

The scanner is deterministic triage, not proof. Its JSON output includes a versioned scan receipt and exact input-byte identity. Confirm high-impact findings by reading the relevant files. It must not be used to claim repository-wide correctness, security assurance, or runtime behavior.

## Output contract

Use `references/output-contracts.md` for mode-specific formats. Unless the user requests a different structure, include:

1. assumptions and scope;
2. recommendation or findings with evidence labels;
3. minimal files/changes or next actions;
4. executed validation separately from planned/recommended validation;
5. risks, missing evidence, and material uninspected dependencies.

For findings, prefer the stable shape:

`severity -> code/category -> subject/location -> evidence -> impact -> smallest fix -> validation`

## Stop conditions

Stop, narrow scope, or report a blocker when:

- a required API, schema, permission, policy, or compliance contract is missing and answering would invent it;
- the requested solution places a secret/client secret/service token/private key/password in browser-delivered code;
- the repository/diff is unavailable but the requested conclusion requires evidence about real files;
- a proposed abstraction has no repeated and stable use case;
- a security-sensitive design depends on frontend-only enforcement;
- validation, benchmark, readiness, security assurance, or browser behavior would be claimed without corresponding evidence;
- the next step requires broad repository expansion without a concrete dependency or failure signal;
- two consecutive repair rounds fail to reduce the same objective problem set.
