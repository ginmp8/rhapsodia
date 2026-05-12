# Framework and stack selection

Use this reference when the user asks which React/TypeScript frontend stack to use, especially when AI-maintainability, repository simplicity, or long-term ownership are decision factors.

## Default bias

Prefer the simplest stack that satisfies real requirements. Do not choose a full-stack or server-rendering framework only because it is popular.

## Decision matrix

| option | strong fit | weak fit | AI-maintainability notes |
|---|---|---|---|
| Vite + React | internal SPAs, dashboards, backoffice tools, authenticated apps, static hosting | SEO-heavy public pages, complex server rendering, edge/server actions needed | small surface area, clear client-only model, fast local feedback, fewer framework conventions for agents to learn |
| Next.js | SEO, public pages, server rendering, hybrid server/client work, BFF needs, image/routing platform needs | simple internal app with no SSR/SEO/BFF requirement | powerful but increases context cost through server/client boundaries, caching, routing, and deployment rules |
| React Router framework/data routers | SPAs with strong routing, loaders/actions, nested flows, app-like navigation | teams unfamiliar with route data conventions | good when route ownership is clear; document loader/action contracts carefully |
| TanStack Start | teams already committed to TanStack ecosystem and comfortable with newer full-stack patterns | conservative enterprise apps or teams needing mature conventions | evaluate maturity, deployment constraints, and agent familiarity before adopting |
| Astro | content-heavy sites, marketing pages, docs, partial islands | complex authenticated app workflows | excellent for content boundaries; less direct fit for interactive business apps |

## Recommendation defaults

- For internal backoffice or dashboard apps, recommend Vite + React unless SSR, SEO, or server-side composition is required.
- For public marketing/product pages, evaluate Astro or Next.js depending on interactivity and server needs.
- For authenticated workflow apps, prefer explicit API boundaries over framework magic.
- For teams using AI agents heavily, prefer stacks with fewer hidden lifecycle and deployment rules.

## Questions to resolve

Ask or infer:

1. Is SEO or public page performance a primary requirement?
2. Is server rendering required, or only client-side rendering?
3. Does the frontend need a BFF, server actions, or secure server-side calls?
4. What deployment platform is mandated?
5. Is the app mostly forms, dashboards, content, or interactive product flows?
6. Which libraries and conventions does the team already know?
7. What validation is expected: unit, component, Playwright, visual regression, accessibility, performance?

## Output format

For framework selection, respond with:

1. assumptions;
2. decision matrix comparing 2-4 viable options;
3. recommendation;
4. conditions that would change the recommendation;
5. minimal project structure;
6. validation and migration notes.
