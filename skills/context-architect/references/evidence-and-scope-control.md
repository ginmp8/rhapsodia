# Evidence and Scope Control

## At a Glance

- **Purpose:** Govern repository evidence identity, provenance, source precedence, context selection, budgets, closure, freshness, and unresolved dynamic/external consumers.
- **Load when:** Selecting or pruning repository context, resolving conflicting sources, deciding whether a map is closed/provisional, or reusing evidence across time.
- **Decision impact:** Determines what evidence outranks what, which branches must be searched, when multi-hop expansion stops, how much context is justified, when stale evidence must be refreshed, and when uncertainty must remain explicit.

## Contents

- Evidence identity
- Evidence labels
- Source precedence
- Canonical context-selection order
- Context-selection quality
- Closure criteria
- Context budget
- Freshness and staleness
- Dynamic and external consumers

Use this reference to keep repository context selection reproducible without pretending semantic analysis is fully deterministic.

## Evidence identity

Record enough identity to distinguish one repository state from another:

- repository root or supplied-file boundary;
- revision/HEAD when available;
- dirty-state indicator when available;
- base/head or change-set identity for impact review when available;
- exact primary and critical-secondary paths inspected;
- hashes for reusable maps when the snapshot helper is available;
- evidence tier: `focused`, `standard`, or `extended`.

Do not claim a pinned revision when only a moving branch name was inspected.

## Evidence labels

- `measured`: produced by an executed command or tool.
- `observed`: directly read from current repository bytes/diff.
- `supplied`: provided by the user or external note and not independently verified.
- `inferred`: reasoned from evidence but not directly present.
- `planned`: proposed future state.
- `blocked`: relevant evidence could not be obtained.

Prefer `observed`/`measured` for file selection and validation claims. Keep `supplied` and `inferred` visible when they materially affect scope.

## Source precedence

Use precedence by question, not a single universal ranking.

### What exists now

1. Current repository bytes at the identified revision/worktree.
2. Executed compiler/semantic/build/runtime/tool output tied to that same state.
3. Current generated output plus its generator/source relationship.
4. Current configuration, deployment, lockfile and CI definitions.
5. Tests as evidence of expected behavior.
6. Documentation, issues, comments, ADRs, examples, and history as intent/supporting evidence.

### What should be edited

1. Owning source/contract/schema/generator.
2. Direct hand-written consumers and runtime wiring.
3. Tests/validation artifacts for changed behavior.
4. Derived/generated outputs only through their generator when the repository supports regeneration.
5. Documentation/examples when user-visible or contract-relevant.

When sources disagree, report the conflict. A stale document does not override current code; a generated file does not automatically become the edit owner; a passing test does not prove untested runtime wiring is absent.

## Canonical context-selection order

Expand evidence in this order:

1. exact path/symbol/error/config key/change-set supplied by the task;
2. owning definition/contract/schema/generator;
3. direct semantic consumers/usages/implementations;
4. build/project reverse dependents and runtime registration/configuration;
5. nearest tests/fixtures/contracts;
6. public/data/service boundaries and generated consumers;
7. analogous implementation patterns;
8. deployment, observability, migration, rollback, external dependency versions, and documentation when risk requires them.

Within the same relevance class, prefer stronger evidence source classes from `dependency-tracing.md`, then exact-symbol matches, current-module proximity, and normalized path order. Do not let alphabetical order override dependency direction.

## Context-selection quality

The goal is the smallest evidence set that closes the required branches, not maximum file count.

When a gold/reference set exists (benchmark fixture, known patch context, reviewed map, or explicit expected paths), evaluate selection separately from final implementation:

- `precision = relevant selected / selected`;
- `recall = relevant selected / relevant expected`;
- `F1` as the balance of precision and recall;
- budget compliance or budgeted yield when a token/byte budget is declared;
- unsupported-selection rate for paths not present in the bounded repository evidence;
- no-gold accuracy for cases where the correct outcome is `no-useful-local-context`.

Read `references/context-selection-evaluation.md` when building or interpreting such evaluations. Do not claim these metrics when no gold/reference set exists.

### No-useful-local-context / abstain

If evidence shows that the requested answer is external, missing, generated elsewhere, or not localizable inside the available repository boundary, use `no-useful-local-context` instead of forcing a plausible path. This is a selection outcome, not a failure to search. Record the reason and the next evidence boundary when known.

## Closure criteria

A map is `closed` for its selected tier only when each applicable branch has either evidence or an explicit unresolved status.

### Focused

- owning source identified;
- direct consumers identified;
- nearest validation path identified;
- no evidence of public/schema/security/distributed boundary expansion.

### Standard

Focused plus:

- runtime wiring/config checked;
- build/project ownership or reverse-dependency surface checked when present;
- nearest relevant tests checked;
- one analogous pattern checked;
- direct public/data boundary checked when present;
- one final first-order search/graph pass yields no new in-scope dependency class.

### Extended

Standard plus:

- externally consumed/public/data/service boundaries traced as far as repository evidence permits;
- generated source/consumer relationships checked;
- compatibility/migration/rollout/rollback reviewed;
- security, concurrency/idempotency/ordering, and observability branches considered when relevant;
- dynamic/reflection/config/string-based consumers explicitly searched or marked unresolved;
- external dependency identity and resolved dependency version checked when version-specific API behavior is material;
- selective data-flow/runtime analysis considered when a behavior/source-to-sink question cannot be closed by references alone.

If a required branch cannot be resolved, use `provisional` or `blocked`; do not expand indefinitely to hide uncertainty.

## Context budget

Budget by evidence value, not raw file count or token count.

- Load the smallest section that establishes ownership or a dependency relation.
- Prefer symbol/range reads over entire large files when tools support it.
- Prefer high-confidence semantic/build relations before broad fuzzy retrieval when both are available.
- Do not repeatedly load equivalent implementations once a repository convention is established.
- Keep at most the evidence needed to support the current map branch; summarize low-signal details.
- Escalate from `focused` to `standard` or `extended` when new evidence crosses a risk boundary.
- When a budget is explicit, reserve capacity for owner, direct consumers, runtime/build wiring, and validation before analogous/background context.

Stop searching after closure is satisfied. Continue only when a new risk, conflict, dependency class, or failed validation introduces new evidence needs.

## Freshness and staleness

A reusable map becomes stale when:

- its repository revision changes and the affected graph has not been refreshed;
- a captured primary/critical-secondary file hash changes;
- the base/head change-set identity changes for review-impact;
- a central contract/schema/generator/runtime registration/build graph changes;
- a material lockfile/resolved dependency version changes;
- a previously blocked dependency becomes available;
- implementation discovers a dependency class absent from the approved map.

Refresh leaf branches locally. Refresh the wider graph when a central/public boundary changes. Record map drift explicitly.

## Dynamic and external consumers

Search for reflection, naming conventions, dependency injection, config strings, routes, serializers, messaging topics, SQL object names, generated clients, plugins, and external contracts when relevant. Absence of a static reference is not proof of absence.

For consumers outside available repositories, record the compatibility assumption and treat breaking changes as unresolved until an acceptable contract/versioning strategy exists.
