---
name: frontend-ai-token-efficient
description: use when the primary goal is React/TypeScript frontend AI-maintainability or low-context change safety, including architecture, refactoring/review, frontend runtime validation, browser-side leak prevention, or concise repo guidance; covers Vite, Next.js, React Router, TanStack, Astro, contracts, forms, state, API boundaries, design systems, tests, accessibility, observability, and frontend security. do not use as the primary skill for generic frontend implementation without an AI-maintainability/context concern, pure visual design or branding, native mobile, backend/infrastructure work, or skill creation.
---

# Frontend AI Token Efficient

## Control plane

**Purpose:** Design, review, or guide React/TypeScript frontends so an agent can make correct changes from the smallest sufficient context while humans retain clear ownership, contracts, and validation paths. Efficiency means validated task success first; token/context cost is secondary.

**Use when:** AI-maintainability/context locality is a primary concern, or the request is specifically about frontend architecture/review, runtime validation, browser-side leak prevention, or AI-facing repository guidance owned by this skill.

**Do not use when:** The task is pure backend/infrastructure/native mobile, visual-only design/branding, skill creation, or generic frontend coding where low-context maintainability and this skill's owned safety/runtime concerns are not material.

## Core rules

- Never optimize token or context volume independently of validated task success; reduce required context before reducing code size.
- Existing project conventions win unless evidence shows a correctness, security, coupling, accessibility, or context-cost problem.
- Prefer framework-native locality before imposing a generic folder taxonomy; feature/domain folders are optional, not universal.
- Use summaries/maps/indexes only to orient or localize. Inspect exact source before mutation or exact contract claims.
- Keep ownership explicit. Business rules do not belong in generic `shared` layers; small local duplication is preferable to premature global abstraction.
- Components do not call transport clients directly; use feature/API boundaries, orchestration hooks, schemas, and mappers.
- Never invent an API contract. Read it, request it, or mark it missing/assumed.
- TypeScript types are erased at runtime; validate untrusted runtime boundaries proportionally to risk.
- Frontend authorization is UX only; backend authorization is the security boundary.
- Never put secrets in browser bundles, sensitive session material in web storage by default, or sensitive payloads in logs, analytics, or URLs.
- Preserve the existing visual language, UI library, design tokens, CSS conventions, and component patterns before introducing new aesthetics.
- Separate evidence from recommendation; static reasoning is not executed validation.
- Do not expand repository scope merely to feel comprehensive.

## Mode selection

Choose exactly one primary mode; the primary mode owns the response contract.

| mode | primary intent | direct reference |
|---|---|---|
| `framework-selection` | choose framework/major stack pieces | [framework-selection](references/framework-selection.md) |
| `architecture-plan` | structure, dependencies, ownership, migration | [architecture](references/architecture.md) |
| `implementation-guidance` | plan one concrete change without editing | [implementation-patterns](references/implementation-patterns.md) |
| `code-review` | review diff/PR/component/hook/feature code | [review-checklists](references/review-checklists.md) + implementation reference as needed |
| `ux-flow-review` | implementation-linked forms/onboarding/friction | [ux-quality](references/ux-quality.md) |
| `runtime-validation` | browser/Playwright/screenshots/traces/logs | [runtime-validation](references/runtime-validation.md) |
| `security-review` | frontend leaks/browser trust boundaries | [security](references/security.md) |
| `ai-context-docs` | create/review concise agent-facing repo guidance | [ai-context-docs](references/ai-context-docs.md) |
| `repo-scan` | explicitly requested lightweight local scanner | `scripts/check_frontend_ai_package.py` |

Routing precedence: explicit in-scope mode > browser security/leak risk > requested runtime behavior > code/diff review > architecture > concrete implementation plan > implementation-linked UX > AI-context docs > framework selection. `repo-scan` is supplemental unless explicitly requested. If two modes remain equally primary and would materially change the answer, ask one precise question; otherwise choose the higher-precedence mode and declare the secondary concern.

## Quick workflow

1. Establish target identity, frontend scope, requested outcome, local repository instructions, framework/runtime, and acceptance criteria.
2. Select one primary mode and identify available evidence versus assumptions or missing contracts.
3. Localize with symbols, routes, imports, tests, configs, or concise maps; identify the smallest plausible owner set.
4. Inspect the exact target plus only the contracts needed to change or judge it: imported types/schemas, API boundary, nearest tests, route/provider/config, and design-system primitive when material.
5. Expand only for an observed `dependency`, `contract-owner`, `cross-boundary`, `security-boundary`, `route-config`, `design-system`, or `failing-validation` reason.
6. Load only the direct reference for the selected mode plus [output-contracts](references/output-contracts.md); load [reproducibility](references/reproducibility.md) when evidence comparison, context budgeting, repair loops, or freeze identity matter.
7. Produce the smallest coherent recommendation/finding/change plan; prefer causal fixes and framework-native locality over broad cleanup.
8. Validate at the lowest reliable layer: parse/type/lint/test -> focused runtime/browser checks -> perceptual/manual review when applicable. Keep executed evidence separate from planned checks.
9. On failure: diagnose -> smallest causal fix -> rerun the same gate -> adjacent gates. Stop after two consecutive non-improving repair rounds unless new evidence changes the diagnosis.
10. Freeze after the final pass; any later material edit invalidates affected validation and requires rerun.

## Critical stop rules

Stop, narrow, or report a blocker instead of guessing when a required API/schema/permission/policy/compliance contract is missing; the real repository/diff is unavailable for a file-specific conclusion; the proposal depends on frontend-only authorization; browser-delivered code would contain a secret; validation/security/readiness/runtime behavior would be claimed without evidence; or further context expansion has no concrete dependency/failure signal. Never trade away correctness, safety, contracts, or validation merely to reduce context.

## Expected inputs

Infer only when low-risk and state material assumptions:

1. app type: internal SPA, backoffice, dashboard, public product, content site, or full-stack app;
2. stack and relevant versions;
3. target artifact: structure, feature, component, diff, PR, docs, checklist, security policy, or runtime flow;
4. constraints: design system, API contracts, authentication, sensitive data, compliance, team conventions, tests, deployment, and AI tooling;
5. desired output: recommendation, plan, review, patch guidance, markdown files, scanner report, or validation plan.

## Reference map and progressive loading

Load only branch-relevant detail. The mode table above is the primary one-level discovery surface. Additional cross-cutting references are direct from this root:

- [output-contracts](references/output-contracts.md): stable mode-specific response, finding, severity, and evidence shapes.
- [reproducibility](references/reproducibility.md): evidence labels, exact-source/context budgeting, deterministic ordering, repair/comparison discipline, validation layers, and freeze rules.
- [review-checklists](references/review-checklists.md): architecture, PR, AI-maintainability, UX, runtime, security, documentation, and reproducibility triage.
- [activation examples](examples/activation-scenarios.md): positive, negative, and ambiguous selection examples.
- `evals/activation-scenarios.json`: planned activation coverage; not measured behavior until executed.
- `evals/reproducibility-scenarios.json`: planned regression scenarios; not measured evidence by itself.
- `evals/context-efficiency-scenarios.json`: planned context-locality/runtime/auth scenarios; not measured evidence by itself.

A whole-repository read is not the default. Do not infer repository-wide architecture from top-level folders, summaries, generated maps, or scanner output alone. Reopen/read authoritative source when an exact edit or contract conclusion depends on it.

## Context-efficiency evidence

When context efficiency is material, report the applicable quality gate first, then available cost signals: exact files inspected, orientation sources, expansion reasons/rounds, tokens/context size when observable, tool turns, latency, or monetary cost. Record material uninspected dependencies. A cheaper run that misses required evidence or leaves task success unvalidated is a regression, not an efficiency win.

## Optional scanner

For an explicitly requested lightweight local audit:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format json
```

or:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format markdown --output <report.md>
```

The scanner is deterministic triage, not proof. Its JSON output includes a versioned scan receipt and exact input-byte identity. Confirm high-impact findings by reading the relevant files. Never use scanner output alone to claim repository-wide correctness, security assurance, or runtime behavior.

## Output contract

Use [output-contracts](references/output-contracts.md) for mode-specific formats. Unless the user requests another structure, include assumptions/scope; recommendation or findings with evidence labels; minimal files/changes or next actions; executed validation separately from planned/recommended validation; and risks, missing evidence, and material uninspected dependencies.

For findings, preserve the stable shape:

`severity -> code/category -> subject/location -> evidence -> impact -> smallest fix -> validation`

## Portability contract

Keep the semantic workflow in portable `SKILL.md` plus package-local references/scripts. Host-specific instruction files or metadata are optional adapters only. For repository guidance, keep stable always-on rules in the project's host-neutral/shared instruction surface when practical and task-specific detail in skills/scoped docs. Do not duplicate the same long instruction set across host files; adapters contain only real host differences.

## Detailed stop conditions

Stop, narrow scope, or report a blocker when:

- a required API, schema, permission, policy, or compliance contract is missing and answering would invent it;
- the requested solution places a secret/client secret/service token/private key/password in browser-delivered code;
- the repository/diff is unavailable but the requested conclusion requires evidence about real files;
- a proposed abstraction has no repeated and stable use case;
- a security-sensitive design depends on frontend-only enforcement;
- validation, benchmark, readiness, security assurance, or browser behavior would be claimed without corresponding evidence;
- the next step requires broad repository expansion without a concrete dependency or failure signal;
- a proposed context/token reduction would remove evidence required for correctness, safety, contracts, or validation;
- two consecutive repair rounds fail to reduce the same objective problem set.
