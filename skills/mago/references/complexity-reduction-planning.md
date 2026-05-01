# Complexity Reduction Planning

Load this reference when MAGO plans simplification, de-abstraction, refactoring, or reduction of accidental complexity for a selected spec package.

## Objective

Plan changes that reduce accidental complexity while preserving essential domain behavior. A good plan makes the system easier to understand, change, test, operate, and validate without replacing one speculative abstraction with another.

## Evidence First

Before planning changes, gather or record evidence from repository structure, call flows, tests, incident history, developer feedback, duplicated patterns, change friction, runtime constraints, or user-provided examples. If evidence is missing, record assumptions and open questions instead of presenting preferences as facts.

Classify each complexity candidate:

- needless indirection: interfaces, factories, strategies, adapters, mediators, or pipelines with one real implementation and no credible variation point;
- premature extensibility: generic plugins, configuration switches, reflection, dynamic dispatch, or abstract bases created for hypothetical futures;
- layer explosion: request passes through many thin layers without adding policy, isolation, or domain meaning;
- leaky abstraction: callers must understand internals despite the abstraction;
- over-broad component: module owns unrelated responsibilities and blocks local reasoning;
- misplaced genericity: type parameters or framework patterns obscure simple behavior;
- configuration surface: behavior is hidden behind flags or config without operational need;
- accidental async/eventing: queues, events, retries, or background processing used where direct flow is safer;
- false DRY: shared abstraction couples different concepts that only look similar;
- validation gap: complexity cannot be safely changed because tests or observability are missing.

## Planning Workflow

1. Define the behavior and contracts that must remain stable.
2. Map the current flow: entrypoints, core decisions, dependencies, persistence, integrations, and tests.
3. Identify complexity candidates and classify whether each is accidental, essential, unknown, or out of scope.
4. Rank candidates by impact, risk, reversibility, and validation strength.
5. Choose small simplification hypotheses rather than a broad rewrite.
6. Define the intended end-state in simple language and list what should remain intentionally complex.
7. Slice work for Magia: one seam, abstraction, layer, or flow per executable task when possible.
8. Define validation before execution: characterization tests, existing tests, build/type/lint, smoke checks, contract checks, performance checks, or static reasoning.
9. Define rollback and stopping rules for each slice.
10. Record ADRs only when simplification changes architecture, public contracts, persistence, distribution, operability, or long-term extension policy.

## Decision Heuristics

Prefer removal over replacement when the abstraction has no current value. Prefer explicit code over configurable or dynamic code when variability is not real. Prefer local duplication over shared abstraction when concepts change for different reasons. Prefer boring framework usage over custom meta-frameworks. Prefer improving tests before refactoring high-risk areas.

Do not optimize for line count alone. Useful signals include number of files/types touched to understand one behavior, call-depth hops, number of concepts a maintainer must load, test setup complexity, change failure rate, and ability to validate behavior locally.

## Required Output Shape

A complexity-reduction plan must include:

- scope and selected spec;
- preserved behavior and non-goals;
- evidence inspected and assumptions;
- complexity inventory with classification;
- simplification hypotheses with expected benefit and risk;
- target end-state;
- phased tasks for Magia;
- validation plan per phase;
- rollback and stop conditions;
- ADR or implementation-decision triggers;
- open questions and handoff instructions.

## Handoff to Magia

Each task handed to Magia must be executable without redesigning the PRD: target area, behavior to preserve, abstraction/layer to simplify, allowed write scope, validation checks, expected artifact updates, and conditions that require a technical-gap note back to Mago.
