# Complexity Reduction Execution

Load for simplification, de-abstraction, behavior-preserving refactor, or Mago complexity-reduction plans.

## Objective

Reduce accidental complexity in current code while preserving product intent, observable behavior, contracts, and validation truth. Optimize maintenance, testing, operation, and local reasoning with evidence; not personal style.

## Starting Point

Before editing, identify: target files/modules/flow/task; behavior preserved and allowed to change; simplification hypothesis; complexity evidence; validation safety net; rollback path or smallest reversible step.

If preserved behavior is unknown and no validation path exists, create/request a safety net before deleting abstractions unless the change is trivially local and statically provable.

## Workflow

1. Inspect current flow and conventions.
2. Classify complexity: accidental, essential, unknown, or outside scope.
3. Choose one small step: inline, remove, merge, split, rename, localize, or replace with a simpler existing convention.
4. Prefer deletion/inlining when an abstraction has one real implementation and no current variation point.
5. Preserve public behavior, contracts, persistence, retries, idempotency, ordering, security posture, and observability unless the selected task changes them.
6. Add/update tests when the safety net is weak and the change is not statically obvious.
7. Run narrow validation and record pass/fail/not-run evidence.
8. Document before/after evidence in `complexity-reduction-evidence.md` when structure materially changed.
9. Create `implementation-adr.md` only for durable architecture or extension-policy decisions.
10. Create `technical-gap-note.md` when repository truth contradicts the Mago plan or safe simplification needs a planned-design change.

## Safe Patterns

- Inline pass-through interfaces, services, factories, or adapters with one real implementation and no credible seam value.
- Merge forwarding layers with no policy, isolation, transformation, or domain meaning.
- Replace speculative generic configuration with explicit code when runtime variability is not real.
- Split broad modules only around stable seams and tests.
- Keep local duplication when concepts change for different reasons; avoid false DRY.
- Remove dead extension points only after checking runtime discovery, reflection, configuration, and external contracts.
- Replace custom mini-frameworks with direct framework usage when behavior remains clear and validated.

## Stop

Stop and report blocker/handoff when simplification needs a broad rewrite; behavior equivalence cannot be tested or reasoned honestly; public contracts, data model, security posture, or user-visible behavior would change beyond the task; deletion removes a real security/transaction/resilience/observability/ownership boundary; product or architecture decisions are required first; or validation fails and fixing it exceeds scope.

## Evidence

For each simplification record: before shape including files/types/layers/flow; action taken; preserved behavior/compatibility; executed validation and skipped checks; residual complexity; rollback/recovery; handoff decision `none`, `mago`, `magnomo`, or `both`.
