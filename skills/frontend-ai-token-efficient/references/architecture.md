# Architecture for low-context AI maintenance

## At a Glance

- **Purpose:** Define low-context frontend architecture rules for locality, ownership, dependency direction, API/contracts, state, duplication, and repository structure.
- **Load when:** The primary mode is architecture-plan, or another mode needs a concrete boundary/ownership decision that cannot be resolved from the local source alone.
- **Decision impact:** Constrains module boundaries, feature/shared ownership, allowed dependencies, state location, abstraction promotion, and the architecture evidence expected in the output.
- **Do not load when:** Do not load merely because the repository has folders; load only when structure, ownership, dependency direction, or context locality is material.

## Contents

- Decision principles
- Generic feature/domain shape (optional)
- Framework-native locality adapters
- Dependency rules
- Feature folders
- `shared` rules
- Duplication policy
- API and contract boundaries
- State ownership
- Documentation that reduces context
- Architecture review output

Use this reference when planning or reviewing frontend structure, dependencies, feature boundaries, or repository guidance for AI-assisted coding.

## Decision principles

1. **Framework-native locality first**: prefer the framework's own strongest ownership boundary when it keeps behavior and contracts together.
2. **Locality first**: changing behavior should require reading the owning unit plus a small set of explicit contracts.
3. **Domain ownership**: when a project uses feature/domain layers, business flows belong to their domain owner and generic layers stay domain-neutral.
4. **Explicit boundaries**: imports, API access, schema ownership, and mappers must make ownership visible.
5. **Stable reuse only**: promote code to shared layers only after repeated, stable, domain-neutral use.
6. **Validation as part of architecture**: structure should make typecheck, tests, and runtime validation easy to run locally.

## Generic feature/domain shape (optional)

```txt
src/
  app/
    providers/
    routes/
    config/
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
    account/
      model/
      ui/
      lib/
  shared/
    api/
    ui/
    lib/
    config/
    testing/
```

Use this only when it matches the project's real architecture. Do not create `features/`, `entities/`, or `shared/` merely to satisfy this skill or the scanner. Existing/framework-native conventions win unless they create high coupling, unsafe data flow, or excessive context requirements.

## Framework-native locality adapters

Prefer these locality primitives before introducing a generic taxonomy:

- **Next.js App Router**: keep server-only work on the server and place `'use client'` as low as practical in the tree because it defines the client module boundary. Treat a client boundary expansion as a bundle, security, and context-cost decision.
- **React Router Framework Mode**: route modules can intentionally colocate route component, loader/action, revalidation, and error-boundary behavior. Do not split them into distant layers unless a stable cross-route contract justifies it.
- **TanStack Query**: colocate query keys/functions/options through the project's established query-option factory pattern when it keeps cache identity and transport behavior discoverable together.
- **Vite/client SPA or other stacks**: use the project's existing route/domain/module boundary when it gives one obvious owner and a small validation surface.

Judge locality by the files required to understand and safely change one behavior, not by whether a canonical folder name exists.

## Dependency rules

| layer | may import | must not import |
|---|---|---|
| `app` | routes, features, entities, shared | feature internals unrelated to composition |
| routes/pages | features, entities, shared | transport details unless route-owned |
| `features` | own feature files, entities, shared | other features by default |
| `entities` | own entity files, shared | features, app, routes |
| `shared` | shared only | features, entities with business semantics |

Prefer explicit imports from stable entrypoints. Avoid broad `export *` barrels that hide dependencies or encourage cross-feature coupling.

The table below applies only when the project actually uses this layered feature/domain shape. For framework-native route/module architectures, derive equivalent dependency rules from the framework boundary instead of forcing these folder names.

## Feature folders

A feature folder should answer: what business flow does this implement, what contracts does it depend on, and how do I validate it?

Recommended contents:

```txt
features/<feature>/
  README.md              # scope, owner, dependencies, validation
  api/                   # feature-owned transport calls and types
  components/            # UI pieces local to the feature
  hooks/                 # orchestration hooks, not generic utilities by default
  model/                 # state, reducers, selectors, local domain logic
  schemas/               # form/runtime validation schemas
  tests/                 # unit/component/flow tests close to feature
```

Do not force every folder to exist. Create folders when the feature has real content for them.

## `shared` rules

`shared` is for code that is generic, stable, and domain-neutral.

Good candidates:

- base UI primitives already aligned with the design system;
- HTTP client shell with no endpoint-specific business logic;
- date, number, string, and formatting utilities that are not tied to one domain;
- testing helpers with no feature assumptions;
- config readers that do not expose secrets.

Poor candidates:

- onboarding rules;
- account-opening step decisions;
- permission logic that mirrors backend authorization;
- one-off hooks used by a single feature;
- mappers that encode API details for a specific domain.

## Duplication policy

Small local duplication is often cheaper than a global abstraction. Keep duplication when:

- the repeated code is short and clear;
- each feature may evolve differently;
- the shared abstraction would require reading many files to understand a small change;
- reuse is not yet stable.

Extract only when:

- at least two or three call sites are stable;
- the abstraction has one clear reason to change;
- the new location has an obvious owner;
- tests can verify behavior independent of feature details.

## API and contract boundaries

- Do not call `fetch`, `axios`, GraphQL clients, or SDK clients directly from components.
- Keep transport DTOs close to the API module.
- Map transport data into UI/domain types before rendering.
- Put runtime validation near the boundary when server data cannot be trusted.
- Treat missing API contracts as assumptions, not facts.

Preferred pattern:

```txt
api/get-customer.api.ts       # request and transport call
api/get-customer.types.ts     # DTOs or generated types
api/get-customer.mapper.ts    # DTO -> feature model
hooks/useCustomerForm.ts      # orchestration and view state
components/CustomerForm.tsx   # rendering only
```

## State ownership

Choose the smallest state scope that works:

1. local component state for UI-only state;
2. feature hook or reducer for feature orchestration;
3. URL state for shareable filters, pagination, or navigation state;
4. server-state library for cached remote data;
5. global store only for cross-cutting, stable state.

Avoid global stores as a default. They hide ownership and force agents to inspect more files.

## Documentation that reduces context

Each substantial feature should include a short README:

```md
# <Feature>

## Scope
What this feature owns.

## Dependencies
APIs, entities, shared components, feature flags, permissions.

## Flow
Main user path and important states.

## Contracts
Important request/response, form, and validation assumptions.

## Validation
Commands, tests, and manual/browser checks.

## Do not change without checking
Compliance rules, tracking events, permission behavior, backend contract, or design-system constraints.
```

## Architecture review output

When reviewing architecture, report:

1. current observed structure;
2. context cost: files an agent must read for a typical change;
3. boundary violations or unclear ownership;
4. smallest restructuring that improves locality;
5. validation needed after the change;
6. risks and trade-offs.
