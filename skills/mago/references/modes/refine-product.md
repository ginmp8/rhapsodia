# Refine Product Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- The selected product-only package slice is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected package slice.
- Keep product-only refinement inside `BOARD_ROOT/specs/<spec_id>/`.

## Product Refinement Workflow

1. Read the current product docs first and preserve what is still true.
2. Load only the directly relevant repository facts, discovery evidence, and concept docs needed to resolve current product ambiguity.
3. Tighten or reconcile prd.md, notes.md, and optional validation.md without widening into execution planning.
4. Open ../markdown-writing.md for changed Markdown artifacts and use local scripts for template-backed writes, normalization, and validation whenever prd.md, notes.md, or validation.md needs template reconciliation.
5. Stop once the docs are clearer, internally consistent, and still product-only.

## Boundaries

- do not create or alter tasks.md
- do not decompose work, backfill backlog, infer dependencies, or move the flow toward execution
- do not infer implementation progress, execution status, completion, or rollout state
- keep YAML changes minimal and only when existing repository truth requires documentary alignment without adding task or execution fields
- do not select specialists for future execution unless an existing document already requires a purely documentary metadata field
- leave existing task or execution sections unchanged in this mode

## Refinement Focus

- prd.md: improve clarity of problem framing, audience, goals, non-goals, scope, constraints, hypotheses, risks, and conceptual acceptance criteria while keeping risks and trade-offs synthesized at decision level
- notes.md: tighten decisions, assumptions, trade-offs, risks, open questions, and supporting context without expanding execution-only sections; use it for supporting detail, repository-aware nuance, and rationale behind PRD-level risk/trade-off summaries; omit `Specialist Rationale` and `Execution Log`; legacy execution sections require adapt before use as evidence
- validation.md: refine product-learning questions, validation criteria, and conceptual checks; do not turn it into execution validation
- when the documentation is already coherent, keep the change set minimal
