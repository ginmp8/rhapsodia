# Implementation patterns

Use this reference for concrete frontend implementation guidance: components, forms, state, APIs, mappers, tests, accessibility, performance, and observability.

## Minimal-change process

1. Identify the feature owner and existing pattern.
2. List likely files to read before changing code.
3. Confirm API contracts or mark assumptions explicitly.
4. Keep new code close to the feature until reuse is proven.
5. Add or update tests near the changed behavior.
6. Add browser validation when runtime behavior matters.

## Component rules

Components should focus on rendering and interaction details.

Prefer:

- typed props shaped for display;
- callbacks for actions;
- local UI state for toggles, focus, drafts, and disclosure;
- composition with existing design-system primitives;
- clear loading, empty, error, disabled, success, and permission states.

Avoid:

- direct API calls inside components;
- business rules hidden inside generic UI components;
- components importing unrelated feature modules;
- one component handling fetch, transform, validation, layout, analytics, and permission logic at once.

## Hook rules

Hooks can orchestrate data, form state, and UI behavior, but ownership must stay visible.

Good hook responsibilities:

- combine API calls, mapper output, and view state for one feature;
- expose small command functions to components;
- isolate browser concerns such as focus restoration or media query state;
- keep retry, error, and loading handling consistent.

Bad hook responsibilities:

- becoming a generic dumping ground;
- hiding cross-feature business rules;
- calling unrelated features;
- returning very large objects that force broad rerenders and broad context reads.

## Forms

Form structure should make validation, UX, and API mapping explicit.

Recommended files:

```txt
features/<feature>/schemas/<form>.schema.ts
features/<feature>/model/<form>.defaults.ts
features/<feature>/api/<operation>.mapper.ts
features/<feature>/hooks/use<form>.ts
features/<feature>/components/<Form>.tsx
```

Guidelines:

- Use schema validation for user input and runtime boundaries.
- Keep transport payload mapping separate from form rendering.
- Keep labels visible; placeholders are examples, not labels.
- Show errors close to fields and preserve input on submit failure.
- Focus the first invalid field after submit.
- Split long forms into steps only when it reduces cognitive load or supports saved progress.
- Do not collect a field just because it might be useful later; tie it to value, compliance, or backend requirement.

## API layer

Use an API layer for transport and contract handling.

```txt
api/create-application.api.ts      # HTTP call
api/create-application.types.ts    # DTOs or generated types
api/create-application.mapper.ts   # feature model <-> API payload
api/create-application.errors.ts   # optional error mapping
```

Rules:

- Components do not call HTTP clients directly.
- Mappers own transformation between UI/domain models and transport DTOs.
- Do not invent unknown fields. Use TODO or assumption notes when contract is unavailable.
- Normalize API errors into UI-friendly states.
- Do not leak raw backend errors to users or logs when they may contain sensitive data.

## State selection

| need | preferred state |
|---|---|
| local input, toggle, open/closed state | component state |
| feature workflow state | feature hook or reducer |
| server cache, refetch, stale data | server-state library |
| shareable filters, tabs, pagination | URL state |
| authenticated user shell, theme, stable app-wide preferences | global store/provider |

Do not introduce global state to avoid prop passing for one feature. Global state increases the number of files an agent must inspect.

## Design-system usage

In existing products:

- reuse current UI library and tokens;
- inspect similar screens before creating new components;
- preserve spacing, typography, colors, radius, elevation, motion, and interaction conventions;
- create wrappers only when the team already uses that pattern or when repeated design-system usage is error-prone.

When no design system exists:

- define a small token set first;
- choose one layout strategy;
- define accessible focus, disabled, error, loading, and empty states;
- avoid one-off styles that cannot be reused.

## Accessibility defaults

Check at least:

- semantic HTML before ARIA;
- visible focus;
- keyboard navigation;
- labels and descriptions for inputs;
- modal focus trap, escape behavior, and return focus;
- screen reader announcements for dynamic errors and success states;
- contrast and touch target size;
- reduced motion where animation may distract or harm.

## Performance defaults

Prioritize simple performance wins before advanced tuning:

- keep route and feature boundaries clear;
- avoid unnecessary global renders;
- lazy-load heavy routes or charts when useful;
- memoize only after evidence of rerender cost;
- avoid shipping unused component libraries or icon packs;
- track bundle impact when adding major dependencies.

## Observability and analytics

Frontend observability should help diagnose user-impacting behavior without leaking data.

Recommended events:

- flow started/completed/abandoned;
- field-level error counts without raw field values;
- API failure category, not sensitive payload;
- retry and timeout counts;
- browser/runtime error boundaries;
- performance markers for important flows.

Rules:

- Never log secrets, tokens, documents, raw personal data, financial data, or full API payloads.
- Redact or hash identifiers only when approved by policy.
- Keep event names stable and documented.
- Put analytics behind a small wrapper so sensitive fields can be blocked centrally.

## Testing pattern

Use the lowest-cost test that catches the risk:

- pure functions, mappers, reducers, and schemas: unit tests;
- components with conditional states: component tests;
- forms, modals, routing, permissions, responsiveness, and browser APIs: Playwright or equivalent browser validation;
- accessibility and keyboard behavior: automated smoke plus manual review where needed.

## Implementation guidance output

When guiding implementation, provide:

1. assumptions;
2. minimal file set to inspect or change;
3. step-by-step implementation plan;
4. contract assumptions and data boundaries;
5. validation commands and browser checks;
6. risks and rollback notes.
