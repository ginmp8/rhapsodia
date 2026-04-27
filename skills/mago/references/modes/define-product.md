# Define Product Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- The selected product-only package slice is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected package slice.
- Keep product-only outputs inside `BOARD_ROOT/specs/<spec_id>/`.

## Product Definition Workflow

1. Load only the directly relevant product context: the request, discovery evidence, existing concept docs, and repository facts that shape users, scope, constraints, or risks.
2. Produce the smallest truthful product documentation set: prd.md, notes.md, and optional validation.md.
3. Create or reconcile YAML only when an existing sequential container truly requires it and the required values are already justified by evidence.
4. Open references/markdown-writing.md for changed Markdown artifacts and use `scripts/write_artifact_scaffold.py` plus `scripts/validate_artifact.py` when prd.md, notes.md, or validation.md is template-backed.
5. Stop once the idea is clear enough for later planning without inventing execution detail.

## Boundaries

- do not create or alter tasks.md
- do not define backlog, execution order, implementation phases, dependencies, rollout work, or execution status
- do not infer implementation progress, completion, or blocker state
- do not select specialists for future execution unless an existing document already requires a purely documentary metadata field
- do not create manifest.yaml or spec-catalog.yaml unless repository truth makes that registration indispensable and the needed values already exist
- if current docs already contain task or execution sections, leave them unchanged in this mode

## Document Focus

- prd.md: clarify problem, audience, context, goals, non-goals, scope, constraints, risks, hypotheses, and conceptual acceptance criteria as current evidence supports; keep risks and trade-offs synthesized at decision level
- notes.md: record decisions, assumptions, trade-offs, risks, and open questions without adding execution-log or execution-specialist noise; use it for supporting detail, repository-aware nuance, and rationale behind PRD-level risk/trade-off summaries; omit `Specialist Rationale` and `Execution Log` unless truthful existing sections must be preserved
- validation.md: use only for product validation questions, hypothesis checks, or conceptual acceptance criteria; not for runtime or implementation test planning
- when the input is incomplete, prefer a smaller truthful document set over invented structure
