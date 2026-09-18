# Discovery Mode

## Canonical Rules

- `BOARD_ROOT` is required for discovery artifacts and must contain `cycle.yaml`.
- Use prompt-provided `BOARD_ROOT` when present; otherwise derive it from canonical-paths.md with concrete `board_id`, `year`, and `cycle_id`.
- No spec package path or registry identity is active in `discovery`.
- Keep discovery-state.json, discovery-index.yaml, and `candidates/` under `BOARD_ROOT` only.
- Old layouts are read-only inputs to `adapt`, never discovery write targets.

Use this mode for iterative repository scanning. It is the upstream evidence stage that feeds `order`; it is not a loose brainstorming pass.

## Discovery Workflow

1. Select or create the resolved `BOARD_ROOT` from `references/canonical-paths.md`, containing cycle.yaml, discovery-state.json, discovery-index.yaml, and candidate docs under `candidates/`.
2. Load only the current frontier batch, existing discovery artifacts, and repository facts needed to classify what those files reveal.
3. Update discovery-state.json with frontier progress, file coverage, and next-frontier decisions.
4. Update discovery-index.yaml with stable candidate entries and candidate status transitions.
5. Create or reconcile candidate docs only for materially distinct capability boundaries.
6. Stop after the current bounded frontier batch is truthfully captured; discovery is iterative by design.

## Discovery Boundaries

Discovery is authoritative only for upstream evidence such as:

- frontier analysis
- candidate repository evidence
- provisional capability boundaries
- entrypoints, supporting files, and migration-relevant findings

Discovery must not assign:

- `spec_id`
- `cycle_id`
- `feature_version`
- priority, dependency order, or `order_hint`

Discovery must not create:

- registry records
- generated spec-catalog.yaml or define-queue.yaml projections
- define package artifacts such as manifest.yaml, prd.md, technical-design.md, tasks.md, notes.md, or validation.md

## Provisional Identity

When a likely capability boundary exists, prefer a provisional `feature_key` that is:

- lowercase
- kebab-case
- stable enough to survive ordering

Do not force a provisional id when the boundary is still ambiguous. Discovery records capability evidence; `order` creates immutable spec identity.

## Discovery Artifacts

Use the canonical discovery artifact set from `references/artifacts/discovery-order.md`:

- discovery-state.json for frontier loop state and file coverage
- discovery-index.yaml for machine-readable candidate inventory
- {BOARD_ROOT}/candidates/<candidate_id>.md for per-candidate evidence and capability details

Keep shared index entries concise and keep detailed evidence in candidate docs.

## Candidate Lifecycle

- use `new` when a candidate first appears with enough evidence to name it
- use `updated` when new evidence materially changes an existing candidate
- use `provisional` when the boundary still exists but remains too ambiguous for ordering
- use `ready_for_order` when the candidate has enough stable boundary and evidence to enter `order`
- use `blocked` when further discovery cannot proceed honestly without new evidence or access
- use `duplicate` only when another candidate already owns the same capability boundary

## Promotion and Handoff

Use discovery to decide whether work should stay upstream or move downstream.

Hand off downstream only when the evidence is strong enough:

- stay in discovery if boundaries are still ambiguous
- move to `order` when discovery can support identity, dependency, priority, and package-shape judgment for new work
- move to `refine` only when an already-defined registry-backed package stays valid and needs bounded documentation updates

Do not skip `order` for new package creation, and do not use discovery to fake certainty that belongs to later phases.

## Blockers

If the frontier is blocked:

- record the blocker explicitly
- preserve the evidence gathered so far
- avoid inventing boundaries, identities, dependencies, or ordering facts to keep momentum

Truthful ambiguity is better than unstable structure.
