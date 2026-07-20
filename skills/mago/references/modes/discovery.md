# Discovery Mode

## Purpose

Inspect repository evidence in bounded batches and maintain upstream discovery state without inventing planning identity, order, or implementation truth. Discovery feeds `order`; it is not a brainstorming substitute.

## Canonical Rules

- Resolve one canonical `BOARD_ROOT` containing `cycle.yaml`.
- No spec package is active in discovery.
- Keep `discovery-state.json`, `discovery-index.yaml`, and `candidates/` under the cycle root.
- Old layouts are read-only inputs to `adapt`, never discovery write targets.

## Workflow

1. Resolve the active cycle and current discovery frontier.
2. Load only the current frontier batch, existing discovery state/index, relevant candidate docs, and repository facts needed to classify that batch.
3. Inspect entry points, contracts, tests, schemas, configuration, behavior paths, dependencies, and migration-relevant evidence.
4. Update `discovery-state.json` with scanned paths, frontier progress, coverage, blockers, and next-frontier decisions.
5. Update `discovery-index.yaml` with concise stable candidate entries and lifecycle transitions.
6. Create or reconcile candidate docs only for materially distinct capability boundaries; keep detailed evidence in candidate docs.
7. Stop after one truthful bounded iteration and validate discovery artifacts/board.

## Boundaries

Discovery may own frontier analysis, candidate evidence, provisional capability boundaries, entry points, supporting files, confidence, unknowns, and suggested next steps.

Discovery must not assign cycle/spec identities, semantic versions, dependencies, lifecycle status, priority, or order. It must not create registry records, generated views, package directories, PRDs, designs, tasks, notes, validation plans, or execution evidence.

## Provisional Identity

A candidate may suggest a lowercase kebab-case `feature_key` only when the capability boundary is stable enough. Candidate IDs remain discovery-local and never become `spec_id`. Do not force provisional identity when the boundary is ambiguous.

## Candidate Lifecycle

- `new`: enough evidence exists to name the candidate;
- `updated`: new evidence materially changes it;
- `provisional`: a likely boundary exists but is not registration-ready;
- `ready_for_order`: boundary and evidence are stable enough for an independent registry record;
- `blocked`: progress requires unavailable evidence or access;
- `duplicate`: another candidate owns the same capability boundary.

## Promotion and Failure Policy

Move new work to `order` only when evidence supports a stable capability boundary and dependency/handoff judgment. Use `refine` only for an already-defined canonical package. Do not skip registration for new packages.

When blocked, record the blocker, preserve confirmed evidence, and stop rather than inventing boundaries or sequencing facts. Truthful ambiguity is preferable to unstable structure.
