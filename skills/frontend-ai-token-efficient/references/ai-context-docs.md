# Short documentation for AI agents

Use this reference to create or review repository files that guide AI agents. Keep guides short, practical, and tied to real project decisions.

## Recommended files

```txt
AI_CONTEXT.md
ARCHITECTURE.md
CONVENTIONS.md
DEPENDENCY_RULES.md
TESTING_GUIDE.md
API_GUIDE.md
UI_GUIDE.md
SECURITY_FRONTEND.md
UX_GUIDE.md
RUNTIME_VALIDATION.md
AGENTS.md or .github/copilot-instructions.md when the team's tool supports them
*.agent.md when specialized agents are versioned in the repo
```

Create only files that will contain useful guidance. A short guide that agents actually read is better than long documentation that gets ignored. For tools that support file-level instructions or agents, keep those files versioned, small, and aligned with the same contracts as this skill.

## `AI_CONTEXT.md` template

```md
# AI Context

## Goal
This project prioritizes local changes, low coupling, and readability.

## Structure
- app/: bootstrap, providers, and routes
- features/: business flows
- entities/: reusable domain entities
- shared/: generic code with no business rules

## Rules for changes
1. Before changing a feature, read that feature's README.
2. Do not create global abstractions without at least two stable use cases.
3. Do not place business rules in shared/.
4. Do not call HTTP directly from components.
5. Update tests and validation notes with the change.

## Security
- Do not add secrets to public environment variables.
- Do not store sensitive tokens in localStorage or sessionStorage.
- Do not log payloads with personal, financial, or authentication data.

## Validation
- Run typecheck and affected tests.
- Use browser validation for flows with focus, modal, form, responsive, or visual behavior.
```

## `ARCHITECTURE.md` template

```md
# Frontend Architecture

## Principles
- Feature-first organization.
- Explicit contracts at boundaries.
- Small local duplication is acceptable.
- Shared code must be generic and domain-neutral.

## Dependency rules
Allowed:
- app -> pages/routes -> features -> entities -> shared
- features -> entities/shared
- entities -> shared
- shared -> no feature imports

Avoid:
- feature -> feature imports
- components calling APIs directly
- global stores that hide feature ownership

## Folder shape
```txt
src/
  app/
  features/
    account-opening/
      api/
      components/
      hooks/
      model/
      schemas/
      tests/
      README.md
  entities/
  shared/
    api/
    ui/
    lib/
```
```

## `CONVENTIONS.md` template

```md
# Conventions

## Naming
- Feature folders use kebab-case.
- Components use PascalCase.
- Hooks start with use.
- API files end with .api.ts.
- Mappers end with .mapper.ts.

## Components
- Components render UI and receive already-shaped props.
- They do not fetch data directly.
- They do not own cross-feature business rules.

## Forms
- Schema and mapper stay close to the feature.
- Field errors are specific and close to the field.
- Submit preserves user input and focuses the first error.

## Comments
Prefer comments for non-obvious decisions, constraints, or compliance rules. Do not comment obvious code.
```

## `DEPENDENCY_RULES.md` template

```md
# Dependency Rules

## Allowed dependencies
| from | may import |
|---|---|
| app | pages, features, entities, shared |
| pages/routes | features, entities, shared |
| features | entities, shared |
| entities | shared |
| shared | shared only |

## Forbidden dependencies
- shared importing from features.
- entities importing from features.
- feature-to-feature imports unless routed through a deliberate composition point.
- UI components importing API clients directly.

## When in doubt
Keep logic local until reuse is stable, explicit, and domain-neutral.
```

## `TESTING_GUIDE.md` template

```md
# Testing Guide

## Default checks
- Typecheck.
- Unit tests for pure logic, schemas, mappers, and hooks.
- Component tests for conditional rendering and interaction.
- Playwright for real flows, routing, modals, focus, forms, accessibility smoke checks, and responsiveness.

## Evidence
Each change should state:
- commands executed;
- relevant results;
- tests not run and why;
- remaining manual validation.
```

## `API_GUIDE.md` template

```md
# API Guide

## Rules
- Do not invent payloads or response shapes.
- Keep transport types near api/.
- Map transport data into UI/domain-friendly shapes before rendering.
- Handle loading, error, empty, permission, and retry states explicitly.

## File pattern
```txt
features/<feature>/api/<operation>.api.ts
features/<feature>/api/<operation>.types.ts
features/<feature>/api/<operation>.mapper.ts
```
```

## `UI_GUIDE.md` template

```md
# UI Guide

## Existing project
- Reuse the design system, component library, tokens, layout rules, and accessibility patterns.
- Do not introduce new fonts, color palettes, animation libraries, or component systems without a product and technical reason.

## New UI without design system
- Define tokens for color, spacing, typography, radius, elevation, and motion.
- Choose a clear visual direction based on the product context.
- Keep hierarchy, responsiveness, and accessibility measurable.
```

## `SECURITY_FRONTEND.md` template

```md
# Frontend Security

## Never do this
- Put secrets, private keys, client secrets, service tokens, or passwords in frontend code or public environment variables.
- Store sensitive tokens in localStorage or sessionStorage.
- Rely on frontend checks as real authorization.
- Send sensitive payloads to logs, analytics, URLs, or third-party tools.

## Required checks
- Public environment variable review.
- Storage review.
- Logging and analytics review.
- XSS and HTML rendering review.
- CSP and source map posture review for production.
```

## `RUNTIME_VALIDATION.md` template

```md
# Runtime Validation

Use browser validation when static review is insufficient.

## Validate with Playwright when changing
- forms and validation;
- modals, focus, escape, and keyboard navigation;
- responsive layout;
- protected or permission states;
- visual states such as loading, empty, error, success, and disabled;
- routing and redirects.

## Evidence to capture
- command;
- browser and viewport;
- screenshots when useful;
- console and network errors;
- accessibility notes;
- known gaps.
```

## Writing rules for AI-facing docs

- Start with the decision, then the reason.
- Prefer tables and short rules over long prose.
- Keep examples realistic and project-specific.
- Mark assumptions explicitly.
- Avoid generic framework tutorials.
- Keep one source of truth for dependency rules and reference it from other docs.
- Update docs only when they change future behavior.
