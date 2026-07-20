# Define Product Mode

## Canonical Rules

- Resolve one canonical `BOARD_ROOT`, registry record, and package path `BOARD_ROOT/specs/<spec_id>/`.
- Keep product-only outputs inside the selected package.
- Registry identity, dependencies, handoff, generated views, tasks, and execution state are read-only in this mode.

## Product Definition Workflow

1. Load the request, linked discovery evidence, existing concept docs, registry context, and repository facts that shape users, scope, constraints, or risks.
2. Produce the smallest truthful set: `prd.md`, `notes.md`, and optional `validation.md`.
3. Use templates/scripts when files need creation or structural normalization.
4. Keep product validation conceptual; do not introduce runtime test results.
5. Stop when the product boundary is clear enough for later task definition without inventing execution detail.

## Boundaries

- do not create or alter `tasks.md`, manifest identity, registry data, dependencies, generated views, or execution records;
- do not define backlog order, implementation phases, rollout state, completion, or execution blockers;
- do not select execution specialists except for a pre-existing documentary field;
- if old task/execution sections are mixed into product docs, route through `adapt` instead of normalizing them here.

## Document Focus

- `prd.md`: problem, audience, context, goals, non-goals, scope, constraints, risks, hypotheses, and conceptual acceptance criteria;
- `notes.md`: planning decisions, assumptions, trade-offs, risks, evidence references, and open questions; no execution log;
- `validation.md`: product-learning questions, hypothesis checks, and conceptual acceptance criteria only.

Prefer a smaller truthful document set over invented structure.
