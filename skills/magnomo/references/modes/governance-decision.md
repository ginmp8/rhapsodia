# Governance Decision Mode

Use `governance-decision` only for Magnomo governance decisions. `governance-decisions.md` is a governance decision filename, not an Architecture Decision Record.

## Canonical Rules

Requires `BOARD_ROOT` for repository-facing writes. Use prompt `BOARD_ROOT` after validation; otherwise derive it from `references/canonical-paths.md`. Keep `governance-decisions.md` directly under `BOARD_ROOT`.

Create the file with `scripts/write_artifact_scaffold.py <BOARD_ROOT>/governance-decisions.md` when absent. Append with `scripts/append_governance_decision_entry.py`; do not treat it as an Architecture Decision Record writer. Preserve history; corrections, deprecations, and supersessions are new dated entries. Missing decision makers, links, or alternatives stay `unknown`, `none`, or explicit unknown prose. Validate with `scripts/validate_artifact.py <BOARD_ROOT>/governance-decisions.md`.

## Entry Meaning

- `Status`: `accepted`, `superseded`, `deprecated`, or `corrected`.
- `Decision`: governance/delivery decision made.
- `Context`: delivery, roadmap, stakeholder, ownership, risk, or handoff facts requiring a decision.
- `Reason`: why this governance option was chosen.
- `Alternatives`: governance options considered or `none`.
- `Impact`: change to roadmap bookkeeping, delivery, stakeholders, or handoff.
- `Decision Maker`: person, group, role, or `unknown`.
- `Links`: related RFC, roadmap, spec, ticket, PR, meeting note, Mago/Magia evidence, or `none`.
- `Supersedes`: previous governance decision reference or `none`.

Link Mago `technical-design.md` or Magia execution artifacts only as supporting evidence when the governance decision depends on them. Do not edit or restate technical docs as governance source of truth.
