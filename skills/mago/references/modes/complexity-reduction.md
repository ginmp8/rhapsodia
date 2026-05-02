# Complexity Reduction Mode

Use this mode when MAGO must plan simplification, de-abstraction, refactoring strategy, or reduction of accidental complexity for one selected spec package.

## Required Inputs

- `BOARD_ROOT`, `board_id`, `cycle_version`, and `spec_id`.
- Repository evidence or explicitly marked assumptions about the complex area.
- Behavior, contracts, or invariants that must be preserved.
- Complexity symptoms: unnecessary abstraction, layer explosion, genericity, configuration surface, leaky abstraction, false DRY, or validation gap.
- Risk tolerance and validation expectations.

## Outputs

Create or update complexity-reduction-plan.md and, when useful, align execution-handoff-plan.md, tasks.md, validation.md, technical-design.md, or planned ADRs. Do not edit code. Do not claim runtime behavior or implementation results.

## Workflow

1. Load `references/complexity-reduction-planning.md`.
2. Identify behavior to preserve and non-goals.
3. Inventory complexity candidates and classify them as accidental, essential, unknown, or out of scope.
4. Select small simplification hypotheses with evidence, expected benefit, blast radius, validation, and rollback.
5. Slice tasks so Magia can execute one reversible simplification at a time.
6. Define validation gates before execution.
7. Add ADRs only for material architecture or extension-policy decisions.
8. Record assumptions and blockers rather than inventing repository truth.

## Stop Conditions

Stop when the request is purely taste-based, lacks evidence and cannot be framed as an assumption, requires broad code rewriting, or requires current runtime evidence that only Magia can produce.
