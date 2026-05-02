# Roadmap Mode

Use for `roadmap-define`, `roadmap-refine`, and `roadmap-to-specs`.

## Canonical Rules

`BOARD_ROOT` is required for repository-facing roadmap artifacts. Prompt `BOARD_ROOT` wins after validation; otherwise derive it from `references/canonical-paths.md`. A linked spec path is optional read-only context when `roadmap-to-specs` references one selected spec path. Keep roadmap artifacts directly under `BOARD_ROOT`.

Create/refresh roadmap artifacts with local scripts when possible. Use `scripts/write_artifact_scaffold.py` for scaffolds and `scripts/validate_artifact.py` for validation; do not copy or manually check template text when a script can do it.

Roadmap is upstream human intent: initiatives, feature candidates, MVP boundaries, sequencing, dependencies, risks, and candidate spec handoffs.

## roadmap-define

Create/update `roadmap.yaml`, `roadmap.md`, and `feature-map.yaml` when candidates are ready for handoff. Use `rfc-proposal` for undecided material roadmap proposals and `adr-record` for accepted material roadmap changes.

Capture initiative context, owner, goals, outcomes, feature candidates, MVP boundaries, non-goals, sequencing (`now`, `next`, `later`, `future`), dependencies, risks, assumptions, constraints, open decisions, stakeholders, and decision makers when known. Preserve missing owners, dates, stakeholders, and confidence as unknown.

## roadmap-refine

Update an existing roadmap when priorities, sequencing, confidence, scope, dependencies, MVP boundaries, or readiness for Mago changes.

Rules: preserve stable `feature_key` values unless rename is explicitly decided and recorded; keep `roadmap.yaml`, `roadmap.md`, and `feature-map.yaml` consistent; append every decided material change to `adr-records.md`; keep undecided material changes in `rfc-proposals.md` or `roadmap.md` `Open Decisions`; keep historical decision entries append-only except dated corrections.

Material changes include MVP boundary, sequencing, dependency, commitment, confidence, `ready_for_spec`, `candidate_spec_id`, owner, stakeholder, or decision-maker changes.

## roadmap-to-specs

Prepare candidate Mago handoffs by creating/updating `feature-map.yaml` only.

Do: generate handoff entries with `feature_key`, `candidate_spec_id`, `title`, `scope_summary`, `dependencies`, and `recommended_mago_mode`; use source context from Magnomo roadmap artifacts; recommend Mago mode such as `define`, `refine`, or `split` when clear; mark unresolved candidates `ready_for_spec: false` or `candidate_spec_id: null`.

Do not create/modify Mago spec packages, write Mago files, or generate acceptance criteria, implementation tasks, repository steps, or validation plans.
