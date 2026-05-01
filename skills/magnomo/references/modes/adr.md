# Governance Decision Mode

Use for `governance-decision`. The legacy mode name `adr-record` and file name `adr-records.md` are retained only for compatibility with existing scripts and historical board files.

This mode does not create Architecture Decision Records. Architecture Decision Records belong to Mago for planned/spec decisions and to Magia for execution-grounded implementation decisions.

Use this mode after a material governance decision exists and future readers need to understand why the roadmap bookkeeping, delivery posture, ownership, stakeholder alignment, accepted business risk, due date, or Mago handoff changed.

Do not use this mode for unresolved technical proposals, implementation task planning, code-only architecture decisions, Mago technical design authoring, Mago ADRs, or Magia execution decisions. Use `rfc-proposal` while a governance decision is still under review.

## Rules

- `BOARD_ROOT` is required.
- Keep `adr-records.md` directly under `BOARD_ROOT` only as a legacy governance decision log filename.
- Create the file with `scripts/write_artifact_scaffold.py <BOARD_ROOT>/adr-records.md` when it does not exist.
- Append entries with `scripts/append_adr_entry.py`; treat the script as a governance decision writer, not an architecture ADR writer.
- Preserve historical entries. Corrections, deprecations, and supersessions are new dated entries, not rewrites.
- Use `unknown`, `none`, or explicit unknown prose for missing decision makers, links, or alternatives.
- Validate with `scripts/validate_artifact.py <BOARD_ROOT>/adr-records.md`.

## Required Entry Meaning

- `Status`: `accepted`, `superseded`, `deprecated`, or `corrected`.
- `Decision`: what governance/delivery decision was made.
- `Context`: the delivery, roadmap, stakeholder, ownership, risk, or handoff facts that made the decision necessary.
- `Reason`: why this governance option was chosen over available alternatives.
- `Alternatives`: governance options considered or `none`.
- `Impact`: what changes for roadmap bookkeeping, delivery, stakeholders, or handoff.
- `Decision Maker`: person, group, role, or `unknown`.
- `Links`: related RFC, roadmap, spec, ticket, PR, meeting note, Mago/Magia evidence, or `none`.
- `Supersedes`: previous governance decision reference or `none`.

When a Mago `technical-design.md` or Magia execution artifact exists, link it as supporting evidence only when the governance decision depends on it. Do not edit or restate the technical document as the governance source of truth.

