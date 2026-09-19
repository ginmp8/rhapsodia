# Evidence and Scope Control

Use this reference to keep repository context selection reproducible without pretending semantic analysis is fully deterministic.

## Evidence identity

Record enough identity to distinguish one repository state from another:

- repository root or supplied-file boundary;
- revision/HEAD when available;
- dirty-state indicator when available;
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
2. Executed build/test/runtime/tool output tied to that same state.
3. Current generated output plus its generator/source relationship.
4. Current configuration, deployment, and CI definitions.
5. Tests as evidence of expected behavior.
6. Documentation, issues, comments, ADRs, and examples as intent/history evidence.

### What should be edited

1. Owning source/contract/schema/generator.
2. Direct hand-written consumers and runtime wiring.
3. Tests/validation artifacts for changed behavior.
4. Derived/generated outputs only through their generator when the repository supports regeneration.
5. Documentation/examples when user-visible or contract-relevant.

When sources disagree, report the conflict. A stale document does not override current code; a generated file does not automatically become the edit owner; a passing test does not prove untested runtime wiring is absent.

## Canonical context-selection order

Expand evidence in this order:

1. exact path/symbol/error/config key supplied by the task;
2. owning definition/contract/schema/generator;
3. direct consumers/usages/implementations;
4. runtime registration/configuration and build/package ownership;
5. nearest tests/fixtures/contracts;
6. public/data/service boundaries and generated consumers;
7. analogous implementation patterns;
8. deployment, observability, migration, rollback, and documentation when risk requires them.

Within the same relevance class, prefer exact-symbol matches over fuzzy matches, then current-module proximity, then normalized path order as a tie-breaker. Do not let alphabetical order override dependency direction.

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
- nearest relevant tests checked;
- one analogous pattern checked;
- direct public/data boundary checked when present;
- one final first-order search yields no new in-scope dependency class.

### Extended

Standard plus:

- externally consumed/public/data/service boundaries traced as far as repository evidence permits;
- generated source/consumer relationships checked;
- compatibility/migration/rollout/rollback reviewed;
- security, concurrency/idempotency/ordering, and observability branches considered when relevant;
- dynamic/reflection/config/string-based consumers explicitly searched or marked unresolved.

If a required branch cannot be resolved, use `provisional` or `blocked`; do not expand indefinitely to hide uncertainty.

## Context budget

Budget by evidence value, not raw file count or token count.

- Load the smallest section that establishes ownership or a dependency relation.
- Prefer symbol/range reads over entire large files when tools support it.
- Do not repeatedly load equivalent implementations once a repository convention is established.
- Keep at most the evidence needed to support the current map branch; summarize low-signal details.
- Escalate from `focused` to `standard` or `extended` when new evidence crosses a risk boundary.

Stop searching after closure is satisfied. Continue only when a new risk, conflict, or dependency class appears.

## Freshness and staleness

A reusable map becomes stale when:

- its repository revision changes and the affected graph has not been refreshed;
- a captured primary/critical-secondary file hash changes;
- a central contract/schema/generator/runtime registration changes;
- a previously blocked dependency becomes available;
- implementation discovers a dependency class absent from the approved map.

Refresh leaf branches locally. Refresh the wider graph when a central/public boundary changes. Record map drift explicitly.

## Dynamic and external consumers

Search for reflection, naming conventions, dependency injection, config strings, routes, serializers, messaging topics, SQL object names, generated clients, plugins, and external contracts when relevant. Absence of a static reference is not proof of absence.

For consumers outside available repositories, record the compatibility assumption and treat breaking changes as unresolved until an acceptable contract/versioning strategy exists.
