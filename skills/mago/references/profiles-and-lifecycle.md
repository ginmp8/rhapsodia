# Rigor Profiles and Public Lifecycle

Use this reference before selecting an internal Mago mode. The public surface is intentionally small; profiles control rigor and the lifecycle controls progression. Internal modes remain the execution branches for planning work.

## Deterministic profile selection

Select the least costly profile whose eligibility rules all pass. Escalation is one-way within a run unless new evidence proves the triggering risk was classified incorrectly; never downgrade only to reduce artifacts.

| Profile | Minimum inputs | Required artifacts | Optional artifacts | Mandatory gates | Escalate when | Forbidden shortcuts |
|---|---|---|---|---|---|---|
| `quick` | resolved board/spec identity with matching registry/manifest `profile: quick` or existing package; one repository or bounded file scope; known intended behavior; evidence source; observable validation path | existing registry/manifest identity; one compact planning record in `prd.md` or the already-owned product artifact; bounded `tasks.md`; `validation.md`; assumptions/blockers in the touched artifact | `technical-design.md` only for a small non-material design note; `notes.md` only when facts do not fit safely in the touched artifact | identity/path validation; no duplicate feature; dependency check; complete requirement-to-task-to-validation links for changed behavior; boundary validation | ambiguity remains; public API/event/schema/file contract changes; migration/backfill; security/auth/privacy/compliance impact; operational or rollback complexity; more than one repository/service/team; material architecture decision; irreversible data change; unknown consumer impact | no identity or registry bypass; no omitted validation; no invented repository/runtime evidence; no contract, migration, security, compliance, multi-repository, or material architecture work |
| `standard` | matching registry/manifest `profile: standard`; all quick inputs plus affected components/consumers, constraints, dependencies, compatibility expectation, and explicit acceptance behavior | manifest; `prd.md`; `tasks.md`; `validation.md`; `notes.md`; triggered technical artifacts from the decision matrix | technical design, ADR, contract, migration, observability, operations, security/risk, open questions, execution handoff | package validation; traceability; dependency/duplicate checks; evidence contract; triggered artifact validators; boundary validation | regulated or audit-sensitive work; cross-service or multi-repository coordination; high blast radius; material security/compliance; risky migration; multiple stakeholders with technical decision authority; unresolved critical assumptions | no unexplained optional artifact; no unresolved critical ambiguity at handoff; no compatibility or rollback omission when impact exists |
| `governed` | matching registry/manifest `profile: governed`; all standard inputs plus owners of technical decisions, repository map, affected contracts/data, compliance/security constraints, migration/rollback evidence, operational expectations, and downstream handoff consumers | full standard set plus every artifact triggered by contract, migration, security/risk, observability/operations, architecture decision, and execution handoff; explicit traceability and change-delta sections | only artifacts whose trigger is absent; omission requires recorded rationale | all standard gates; 100% traceability; `validate_plan_quality.py`; v2 relational security validation when triggered; compatibility/migration/rollback review; multi-repository dependency analysis; executable mutation recovery for multi-artifact writes; handoff and reconciliation readiness | no lower profile is allowed while a governed trigger remains | no accepted business risk or governance approval authored by Mago; no runtime pass claims; no manual generated-view edits; no second source of truth; no unlinked requirement, decision, task, or validation |

`quick` is safe minimal planning, not an informal bypass. A request to force `quick` cannot override an escalation trigger.

## Mechanical profile contract

- Registry and manifest carry the same explicit `profile`; missing or conflicting values fail board/package validation.
- `quick` requires manifest, PRD, tasks, and validation. `standard` and `governed` also require notes.
- `standard` and `governed` must decide every conditional artifact in `manifest.yaml.artifact_decisions` as `required` or `not_applicable`, with evidence-backed rationale. Required files must exist; not-applicable files must not exist.
- `quick` may use a bounded technical design, complexity-reduction plan, or open-question queue. Contract, migration, security, operations, observability, or execution-handoff artifacts require escalation.
- A non-clean `mutation_state` blocks handoff and readiness regardless of profile.

## Public lifecycle

Expose this lifecycle to users:

```text
clarify -> define -> analyze -> handoff -> reconcile
```

The lifecycle does not replace internal modes. It maps user intent to one primary mode at a time.

| Stage | Purpose | Typical internal modes | Completion condition |
|---|---|---|---|
| `clarify` | resolve the smallest identity, evidence, behavior, constraint, risk, and profile questions needed for safe planning | read-only preflight; `discovery`; `order`; `prepare-define` | required inputs are resolved or explicit blockers/assumptions prevent writes |
| `define` | create or refine intended technical planning | `define`, `refine`, `define-product`, `refine-product`, `define-tasks`, `refine-tasks`, `technical-design`, `complexity-reduction`, `architecture-decision`, `reshape-tasks`, `adapt` | selected profile artifacts are coherent and canonical |
| `analyze` | check contradictions, duplicate work, dependencies, traceability, evidence gaps, compatibility, migration, security, and profile escalation | read-only validation around the selected primary mode | applicable deterministic gates pass or blockers are reported |
| `handoff` | prepare validated intended work for Magia without claiming execution | selected define/refine mode plus `execution-handoff-plan.md` when triggered | planning package and validation path are sufficient for bounded downstream execution |
| `reconcile` | compare canonical Mago intent with supplied Magia evidence without rewriting either source | read-only reconciliation branch | convergence outcome, deviations, unmet acceptance, obsolete work, and required planning revisions are reported |

A single request may traverse several lifecycle stages sequentially, but every write step still selects exactly one internal primary mode. Do not mix mode ownership in one mutation batch.

## Entry paths

- **Requirements-first:** clarify observable outcomes, write normative requirements and acceptance behavior, then derive design, tasks, and validation.
- **Design-first:** start from an evidenced technical constraint or existing architecture, derive the affected requirements and acceptance behavior, then restore complete traceability before handoff.

Design-first never permits architecture to silently redefine Nomia-owned product intent or accepted business risk.

## User-input reduction

Before asking the user, resolve inputs from the existing board registry, current package, Nomia handoff, repository evidence, and prior validated planning records. Ask only for facts that remain both unresolved and blocking. Do not ask the user to repeat an identifier or constraint already evidenced in the active context.
