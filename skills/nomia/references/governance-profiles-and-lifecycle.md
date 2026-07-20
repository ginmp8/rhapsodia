# Governance Profiles And Lifecycle

Use this reference before choosing a Nomia mode. The profile controls the minimum evidence, approval depth, output depth, and escalation rules. The mode still controls the artifact family.

## Profile Selection

| Profile | Use | Minimum facts | Provenance | Mandatory artifacts | Approval/decision depth | Reporting |
|---|---|---|---|---|---|---|
| `quick` | low-risk intake, clarification, or status-only update | request or selected existing item; known actor/context; known status evidence | source reference for every non-null volatile fact; unknowns remain explicit | no repository artifact is required until canonical identity and path are evidenced; one-line or operational projection is allowed | none unless a material commitment, accepted risk, or due-date/priority change is requested | one-line or operational |
| `standard` | normal delivery governance | board/cycle context for board writes; spec identity for spec writes; requester/owner/stakeholders/dates when known | field-level source or change-event evidence for volatile facts | canonical YAML for the affected scope plus requested projection | material commitment, accepted business risk, priority, owner, scope, or target-date changes require a decision/change record | operational or stakeholder |
| `governed` | regulated, high-risk, executive-visible, contractual, financial, privacy, security, cross-organization, or major stakeholder work | all standard facts plus risk class, decision authority, required reviewers, evidence freshness, and affected commitments | durable field-level provenance, timestamps, actor, rationale, and evidence references | canonical YAML, audit/change record, stakeholder or executive projection, and required handoff envelope | explicit approval/decision evidence; unresolved mandatory approval blocks commitment/release claims | stakeholder, executive, and audit |

### Mandatory escalation from `quick`

Escalate to `standard` or `governed` when the request affects regulation, compliance, financial exposure, privacy, security, contract, legal obligation, production release, accepted business risk, cross-organization ownership, executive commitment, major stakeholder impact, or irreversible/costly action. Escalate when the available evidence is stale, conflicting, or cannot establish the actor or authority for a material change.

`quick` may produce value without all repository identities by returning a non-authoritative draft projection with missing identities marked unknown. It must not write to a canonical board/spec path until the required externally sourced identity and path provenance are resolved.

## Unified User-Facing Lifecycle

Expose the lifecycle below while mapping internally to existing specialist modes:

```text
intake -> triage -> commit -> track -> decide -> close
```

| Lifecycle stage | Typical Nomia modes | Governance result |
|---|---|---|
| `intake` | `delivery-intake`, `roadmap-define`, `rfc-proposal` | capture request, rationale, source, known actors, and unknowns |
| `triage` | `delivery-triage`, `roadmap-refine`, `delivery-portfolio` | classify priority, risk, dependencies, stakeholders, profile, and next authority |
| `commit` | `governance-decision`, `roadmap-to-specs`, `delivery-replan` | record approved commitment, target, ownership, accepted business risk, or Mago handoff readiness |
| `track` | `delivery-status`, `delivery-portfolio`, `feature-report` | report current governance state and attributed planning/execution/validation evidence |
| `decide` | `rfc-proposal`, `governance-decision`, `delivery-replan` | record material changes, acceptance/rejection/deferment, and affected commitments |
| `close` | `release-notes`, `feature-report`, `governance-decision` | record release/closure/cancel/supersede state from current evidence |

The lifecycle is user-facing, not a replacement for artifact modes. Select exactly one mode for each operation and state both the profile and lifecycle stage.

## Context Resolution Before Asking

Search allowed current artifacts before asking the user for board/cycle context, existing spec identity, requester, owner, stakeholders, prior decisions, Mago planning state, or Magia validation state.

Reuse a fact only when all are true:

1. the source is an allowed current artifact or explicit handoff;
2. the fact is unambiguous for the selected governance item;
3. provenance is present;
4. the evidence is within its declared freshness window or has no volatility concern;
5. no newer or conflicting evidence exists.

Otherwise preserve the value as unknown, stale, or conflicting and ask only for the unresolved material fact. Never derive volatile facts from filenames, folder names, role stereotypes, or user intent.

## Profile Output Contract

Every response states:

- selected profile and escalation reason, if any;
- lifecycle stage and exactly one Nomia mode;
- reused facts with provenance and freshness;
- unresolved unknown, stale, or conflicting facts;
- whether the output is canonical or a non-authoritative projection;
- validation and authority boundaries.
