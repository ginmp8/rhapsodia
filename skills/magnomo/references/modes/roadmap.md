# Roadmap Mode

## Canonical Rules

- `BOARD_ROOT` is required for repository-facing roadmap artifacts.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; otherwise derive it from `references/canonical-paths.md`.
- A linked spec path is optional read-only context when `roadmap-to-specs` references one selected spec path.
- Keep roadmap artifacts directly under `BOARD_ROOT`.
- Create or refresh roadmap artifacts with local scripts whenever a script can perform the template-backed operation. Use `scripts/write_artifact_scaffold.py` for scaffold writes and validate with `scripts/validate_artifact.py` instead of copying or checking template text manually.

Use for `roadmap-define`, `roadmap-refine`, and `roadmap-to-specs`.

Roadmap is upstream human intent: initiatives, feature candidates, MVP boundaries, sequencing, dependencies, risks, and candidate spec handoffs.

## roadmap-define

Create or update `roadmap.yaml`, `roadmap.md`, and `feature-map.yaml` when candidates are ready for handoff. Use `rfc-proposal` for undecided material roadmap proposals and `adr-record` for accepted material roadmap changes.

Capture initiative context, owner, goals, outcomes, feature candidates, MVP boundaries, non-goals, sequencing (`now`, `next`, `later`, `future`), dependencies, risks, assumptions, constraints, open decisions, stakeholders, and decision makers when known.

Preserve missing owners, dates, stakeholders, and confidence as unknown.

## roadmap-refine

Update an existing roadmap when priorities, sequencing, confidence, scope, dependencies, MVP boundaries, or readiness for Mago changes.

Rules:

- Preserve stable `feature_key` values unless the rename is explicitly decided and recorded.
- Keep `roadmap.yaml`, `roadmap.md`, and `feature-map.yaml` consistent.
- Append every decided material change to `adr-records.md`; keep undecided material changes in `rfc-proposals.md` or `roadmap.md` `Open Decisions`.
- Keep historical decision entries append-only except for dated corrections.

Material changes include MVP boundary, sequencing, dependency, commitment, confidence, `ready_for_spec`, `candidate_spec_id`, owner, stakeholder, or decision-maker changes.

## roadmap-to-specs

Prepare candidate Mago handoffs by creating or updating `feature-map.yaml` only.

Do:

- Generate handoff entries with `feature_key`, `candidate_spec_id`, `title`, `scope_summary`, `dependencies`, and `recommended_mago_mode`.
- Use source context from Magnomo roadmap artifacts.
- Recommend a Mago mode such as `define`, `refine`, or `split` when the appropriate next planning action is clear.
- Mark unresolved candidates as `ready_for_spec: false` or `candidate_spec_id: null`.

Do not create or modify Mago spec packages, write Mago files, or generate acceptance criteria, implementation tasks, repository steps, or validation plans.
