# Complexity Reduction Execution

Load this reference when MAGIA executes simplification, de-abstraction, behavior-preserving refactoring, or a Mago complexity-reduction plan.

## Objective

Reduce accidental complexity in current code while preserving product intent, externally observable behavior, contracts, and validation truth. The goal is not to make the code match a personal style preference; it is to make future maintenance, testing, operation, and local reasoning easier with evidence.

## Required Starting Point

Before editing, identify:

- target scope: files, modules, flow, or selected Mago task;
- behavior to preserve and behavior explicitly allowed to change;
- simplification hypothesis;
- current complexity evidence;
- validation safety net: tests, build, type checks, lint, characterization tests, contract checks, smoke checks, or static reasoning;
- rollback path or smallest reversible step.

If the behavior to preserve is unknown and no validation path exists, create or request a safety net before deleting abstractions unless the change is trivially local and statically provable.

## Execution Workflow

1. Inspect the current flow and existing conventions before changing code.
2. Classify the complexity: accidental, essential, unknown, or outside scope.
3. Choose one small simplification step: inline, remove, merge, split, rename, localize, or replace with a simpler existing convention.
4. Prefer deletion or inlining when an abstraction has one real implementation and no current variation point.
5. Preserve public behavior, contracts, persistence semantics, retries, idempotency, ordering, security posture, and observability unless the selected task explicitly changes them.
6. Update or add tests when the existing safety net is weak and the change is not statically obvious.
7. Run the narrowest meaningful validation and record pass/fail/not-run evidence.
8. Document before/after evidence in `complexity-reduction-evidence.md` when structure materially changed.
9. Create `implementation-adr.md` only when simplification creates a durable architecture or extension-policy decision.
10. Create `technical-gap-note.md` when the Mago plan is contradicted by repository truth or when the safe simplification requires changing the planned design.

## Safe Simplification Patterns

- Inline a pass-through interface, service, factory, or adapter that has one real implementation and no credible test seam or boundary value.
- Merge thin layers that only forward calls without policy, isolation, transformation, or domain meaning.
- Replace speculative generic configuration with explicit code paths when there is no real runtime variability.
- Split an over-broad module only around stable seams and tests, not around arbitrary architecture categories.
- Keep local duplication when two concepts change for different reasons; avoid false DRY.
- Remove dead extension points after confirming no runtime discovery, reflection, configuration, or external contract depends on them.
- Replace custom mini-framework code with direct framework usage when behavior remains clear and validated.

## Stop Conditions

Stop and report a blocker or handoff when:

- the requested simplification requires a broad rewrite rather than bounded steps;
- behavior equivalence cannot be tested or reasoned about honestly;
- public contracts, data model, security posture, or user-visible behavior would change beyond the selected task;
- deleting an abstraction would remove a real boundary for security, transactionality, resilience, observability, or cross-team ownership;
- the simplification depends on product or architecture decisions Mago must make first;
- validation fails and the fix would expand beyond the selected scope.

## Required Evidence

For each simplification, record:

- before shape: files/types/layers/flow or call depth affected;
- action taken: remove, inline, merge, split, localize, replace, or defer;
- preserved behavior and compatibility;
- executed validation and skipped checks;
- residual complexity and why it remains;
- rollback or recovery path;
- handoff decision: none, Mago, Magnomo, or both.
