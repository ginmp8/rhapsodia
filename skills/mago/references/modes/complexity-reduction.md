# Complexity-Reduction Mode

## Purpose

Produce one evidence-backed simplification, de-abstraction, refactoring, or complexity-reduction plan for a registered spec.

## Required Context

- resolved canonical `BOARD_ROOT`, `cycle_id`, and `spec_id`;
- current package and repository evidence;
- concrete complexity signal, impact, and downstream validation path.

## Workflow

1. Confirm package/registry identity.
2. Diagnose complexity from code, contracts, dependencies, tests, operations, or maintenance evidence.
3. State simplification hypotheses, constraints, trade-offs, migration/rollback expectations, and measurable validation.
4. Create/update the canonical complexity-reduction plan and bounded task slices.
5. Record material planned decisions as ADRs when needed.
6. Validate touched artifacts and package consistency.

## Rules

- planning only; implementation belongs to MAGIA;
- do not recommend broad rewrites without evidence and staged validation;
- preserve behavior, contracts, data, security, and operational constraints explicitly;
- prefer deletion/consolidation over new abstraction when evidence supports it;
- record unknowns and blockers rather than assuming runtime truth.
