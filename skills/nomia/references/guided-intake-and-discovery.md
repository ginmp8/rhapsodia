# Guided Intake And Discovery

Use this reference when the request starts as an idea, incomplete demand, ambiguous status request, discovery conversation, or pre-handoff governance intake.

## Goal

Reach the smallest useful governance record without inventing volatile facts or crossing into technical planning. Guided intake is progressive disclosure, not a second canonical artifact and not an interactive product requirement.

## Intake Order

Ask only what changes the safe next step:

1. **Problem or request**: what condition, pain, obligation, or opportunity needs governance.
2. **Outcome**: what observable business result is expected.
3. **Evidence**: which current source supports the request and when it was observed.
4. **Risk triggers**: regulatory, financial, privacy, security, contractual, executive, cross-organization, irreversible, stale, or conflicting evidence.
5. **Decision need**: what governance decision is required, by whom, and by when.

Requester, owner, target date, stakeholders, dependencies, risks, constraints, scope, and non-goals remain explicit unknowns when not evidenced. Do not ask all questions before producing a safe draft; separate blocking questions from enrichment questions.

## Claim Classification

Keep supplied statements distinguishable:

| Type | Meaning | Governance treatment |
|---|---|---|
| `fact` | attributed observation | retain source, observation time, freshness, authority, and conflicts |
| `opinion` | stakeholder judgment | attribute it; do not promote it to fact |
| `hypothesis` | testable explanation or value expectation | record confidence and invalidation evidence when supplied |
| `commitment` | accountable promise or accepted obligation | require owner/authority, date when material, and change provenance |

## Deterministic Guide

Use:

```bash
python <skill-root>/scripts/guide_intake.py path/to/partial-intake.yaml
python <skill-root>/scripts/guide_intake.py path/to/partial-intake.yaml --output path/to/guidance.json
```

The guide returns a non-authoritative profile, lifecycle, mode, blocking questions, unknowns, escalation reasons, repository-write readiness, possible Mago handoff readiness, next action, and next responsible skill. It never writes canonical governance records and never certifies technical readiness.

## Product Discovery Boundary

Nomia may facilitate problem framing, stakeholder mapping, outcome definition, user/business impact, policy constraints, value hypotheses, success measures, non-goals, open questions, and governance decision framing.

Stop and hand off when the next work requires architecture, stack selection, contracts, technical acceptance criteria, engineering tasks, validation plans, feasibility certification, or implementation. That work belongs to Mago or Magia according to the existing authority split.

## Quick Profile

`quick` may create a minimal non-authoritative intake when work is localized, reversible, well understood, and explicitly low risk. Escalate to `governed` whenever any mandatory trigger applies. Quick intake does not waive identity provenance, stale/conflict handling, state authority, typed handoffs, or validation for repository-facing writes.

## Decision-Ready Output

A decision-ready governance brief contains only attributed governance facts:

- decision required;
- context and outcome;
- business alternatives and criteria when supplied;
- impact and affected stakeholders;
- deadline and authority required;
- business risks and evidence;
- unknowns and conflicts;
- consequence of not deciding when supplied.

Do not manufacture alternatives, technical assessments, or recommendations. Cite Mago or Magia evidence when technical input is required.
