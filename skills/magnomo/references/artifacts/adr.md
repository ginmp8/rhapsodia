# Governance Decision Log Artifact

`adr-records.md` is a legacy filename used by Magnomo for governance decision logs. It is not an Architecture Decision Record artifact.

## Ownership

Magnomo may record delivery, roadmap, owner, stakeholder, due date, accepted risk, release posture, or handoff decisions. Magnomo must not record architecture decisions, implementation decisions, technical designs, code decisions, or execution-grounded ADRs as its own decision.

Architecture Decision Records belong to Mago for planned/spec decisions and Magia for implementation/runtime decisions.

## File

- Board-scoped path: `BOARD_ROOT/adr-records.md`
- Template: [assets/templates/adr-records.md.template](../../assets/templates/adr-records.md.template)
- Writer: `scripts/append_adr_entry.py` as a legacy governance decision writer
- Validator: `scripts/validate_artifact.py`

## Required Sections

Each entry should include:

- Date
- Status
- Decision
- Context
- Reason
- Alternatives
- Impact
- Decision Maker
- Links
- Supersedes

## Boundary Examples

- In scope: PO accepted delivery risk and moved the due date.
- In scope: roadmap item was split before Mago handoff.
- In scope: stakeholder alignment changed the release communication plan.
- Out of scope: use Temporal instead of Kafka consumers.
- Out of scope: implement idempotency by composite key.
- Out of scope: change API contract or persistence model.

