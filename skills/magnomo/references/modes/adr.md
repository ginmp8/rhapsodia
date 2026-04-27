# ADR Mode

Use for `adr-record`.

`adr-record` appends accepted, corrected, deprecated, or superseded governance decisions to `adr-records.md`. Use it after a material decision exists and future readers need to understand why the roadmap, delivery posture, ownership, stakeholder alignment, accepted risk, or Mago handoff changed.

Do not use this mode for unresolved proposals, implementation task planning, code-only architecture decisions, Mago technical design authoring, or Mago/Magia execution decisions. Use `rfc-proposal` while the decision is still under review.

## Rules

- `BOARD_ROOT` is required.
- Keep `adr-records.md` directly under `BOARD_ROOT`.
- Create the file with `scripts/write_artifact_scaffold.py <BOARD_ROOT>/adr-records.md` when it does not exist.
- Append entries with `scripts/append_adr_entry.py`; do not freehand append when the script can represent the record.
- Preserve historical entries. Corrections, deprecations, and supersessions are new dated entries, not rewrites.
- Use `unknown`, `none`, or explicit unknown prose for missing decision makers, links, or alternatives.
- Validate with `scripts/validate_artifact.py <BOARD_ROOT>/adr-records.md`.

## Required Entry Meaning

- `Status`: `accepted`, `superseded`, `deprecated`, or `corrected`.
- `Decision`: what was decided, stated directly.
- `Context`: the forces, constraints, or event that made the decision necessary.
- `Reason`: why this option was chosen over the available alternatives.
- `Alternatives`: options considered or `none`.
- `Impact`: what changes for roadmap, delivery, stakeholders, or handoff.
- `Decision Maker`: person, group, role, or `unknown`.
- `Links`: related RFC, roadmap, spec, ticket, PR, meeting note, or `none`.
- `Supersedes`: previous ADR reference or `none`.

When a Mago `technical-design.md` exists, link it as supporting evidence only when the ADR records a human governance decision. Do not edit or restate the Mago design as the ADR source of truth.
