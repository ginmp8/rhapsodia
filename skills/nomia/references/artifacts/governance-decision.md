# Governance Decision Log Artifact

`governance-decisions.md` is nomia's governance decision-log filename, not an Architecture Decision Record.

## Ownership

May record delivery, roadmap, owner, stakeholder, due date, accepted risk, release posture, or handoff decisions. Must not record architecture, implementation, technical design, code, or execution-grounded ADR decisions as nomia-owned. Architecture Decision Records belong to Mago for planned/spec decisions and Magia for implementation/runtime decisions.

## File

- Board path: `BOARD_ROOT/governance-decisions.md`
- Template: `assets/templates/governance-decisions.md.template`
- Writer: `scripts/append_governance_decision_entry.py` as governance decision writer
- Validator: `scripts/validate_artifact.py`

## Entry Fields

Each entry includes: Date, Status, Decision, Context, Reason, Alternatives, Impact, Decision Maker, Links, Supersedes.

## Boundary Examples

In scope: PO accepted delivery risk and moved due date; roadmap item split before Mago handoff; stakeholder alignment changed release communication. Out of scope: choosing Temporal over Kafka consumers; idempotency by composite key; API contract or persistence-model changes.
