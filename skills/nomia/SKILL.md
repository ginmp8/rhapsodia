---
name: nomia
description: "use when asked to create, update, validate, audit, or report on nomia-owned product and delivery governance: intake, requester, owner, dates, status, stakeholders, roadmap, portfolio, governance decisions, release notes, replanning, and roadmap-to-mago handoffs. do not use for architecture, technical planning, code, tests, deployments, pull requests, magia execution, or engineering decisions except as attributed read-only evidence."
---

# nomia

Nomia owns product/delivery governance and reporting, never software design, engineering decomposition, or technical validation. It writes `business_priority`; generic `priority` is unsupported.

## Distributed ecosystem routing

Use the [routing contract](references/ecosystem-routing-contract.md) and [lifecycle](references/ecosystem-lifecycle.md). Perform only the current governance phase, then hand technical planning to Mago; governed implementation never routes directly to Magia. `scripts/route_ecosystem_request.py` is a read-only owner projection; `scripts/handoff_ledger.py` records authority-neutral transport state.

## Scope and Ownership

- Own: intake, ops/status/stakeholder brief, replanning, portfolio, roadmap/feature map, governance RFC/decisions, release/internal notes, feature report, and roadmap-to-Mago handoff in canonical board/spec locations.
- Never change code, tests, deployments, source control, Mago planning, Magia execution, ADR/technical design, implementation docs/tasks, or technical validation. Consume technical material only as attributed read-only evidence.
- Mago owns cycle/spec identity and planning; Magia owns implementation/validation evidence. Nomia does not require Mago or Magia skill files at runtime.
- Exchange `nomia_to_mago`, `mago_to_nomia`, and `magia_to_nomia` only through the strict [ecosystem handoff contract](references/ecosystem-handoff-contract.md) and `scripts/ecosystem_handoff.py`. Handoffs transfer evidence, not authority.
- Governance decisions may cover scope/sequence/owner/policy/vendor/budget/business-risk/go-no-go/stakeholders; architecture and implementation decisions are handed off.

## Required Inputs

Before repository writes resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, and required `spec_id`. IDs use `cycle-YYYY-MM-DD-cycle-key` and `spec-YYYY-MM-DD-feature-key`; infer year only from a valid cycle ID and reject conflicts. Nomia must not mint planning identities, correct/rename/register them, derive them from legacy IDs, or create/modify registry/package identity. Every identity needs user, typed-handoff, or current-repository provenance such as `candidate_spec_id_provenance`.

Volatile people, dates, status, risk, source-control, decision, acceptance, validation, and release facts require source, observation time, freshness, authority, and no conflict. Otherwise preserve `unknown`, `null`, empty lists, or explicit uncertainty.

## Mode Selection Matrix

Select one profile (`quick`, `standard`, `governed`), one stage (`intake`, `triage`, `commit`, `track`, `decide`, `close`), and exactly one mode. Escalate regulatory, financial, privacy/security, contractual, executive, cross-organization, irreversible, stale, or conflicting work to `governed`.

| Mode | Output |
|---|---|
| `delivery-intake`, `delivery-triage` | intake, ops, status, stakeholder brief |
| `delivery-status`, `delivery-replan` | current status or replanning |
| `delivery-portfolio` | portfolio |
| `roadmap-define`, `roadmap-refine` | roadmap and feature map |
| `roadmap-to-specs` | typed handoff only; existing/evidenced candidate IDs optional |
| `rfc-proposal`, `governance-decision` | governance proposal/decision record |
| `feature-report`, `release-notes` | attributed reports/notes |
| `validate-contracts`, `normalize-human-artifacts` | validation/normalization |
| `governance-adapt` | schema-v2 governance output plus adaptation report from read-only legacy input |

## Progressive Loading

1. [Canonical paths](references/canonical-paths.md), [common governance](references/common-governance.md), [guided intake](references/guided-intake-and-discovery.md), [profiles/lifecycle](references/governance-profiles-and-lifecycle.md), [state/risk/handoffs](references/state-risk-and-handoffs.md), [canonical projections](references/canonical-governance-and-projections.md), then [boundaries](references/contracts.md).
2. Exactly one mode: [delivery](references/modes/delivery.md), [roadmap](references/modes/roadmap.md), [RFC](references/modes/rfc.md), [decision](references/modes/governance-decision.md), [reporting](references/modes/reporting.md), [validation](references/modes/validation.md), or [adapt](references/modes/governance-adapt.md).
3. Load [template integration](references/template-integration.md) and only the affected artifact family: [delivery](references/artifacts/delivery.md), [roadmap](references/artifacts/roadmap.md), [RFC](references/artifacts/rfc.md), [decision](references/artifacts/governance-decision.md), or [reporting](references/artifacts/reporting.md).
4. For handoff/release load [roadmap-to-Mago](references/roadmap-to-mago-contract.md), [priority](references/priority-contract.md), [activation](references/activation-and-evaluation.md), [assurance](references/assurance-and-release.md), and [package validation](references/package-validation.md) only when relevant.

## Execution Workflow

1. Select profile/stage/mode. For incomplete intake, run `scripts/guide_intake.py`; guidance is non-authoritative.
2. Resolve canonical roots/identities and evidence; mark missing/stale/conflicting facts unknown or blocked.
3. Use schema-v2 governance records and keep governance, planning, execution, validation, and release states separate.
4. Use bundled writers/projectors; do not freehand template-backed structures when a script exists.
5. Write only Nomia artifacts. Treat legacy governance as read-only; `scripts/adapt_governance.py` requires externally supplied current identity and never carries/derives old ULID identity.
6. Generate human views with `scripts/project_governance_views.py` as non-authoritative projections containing canonical source, generated/evidence timestamps, unknowns/conflicts/loss, next action, and owner. Use `scripts/project_lifecycle_status.py` for read-only lifecycle status.
7. Build/validate typed v3 handoffs with privacy minimization and causal lineage. Preserve producer version, provenance, freshness, unknowns, conflicts, mapping, and technical authority.
8. Technical completion never closes governance without `scripts/validate_governance_closure.py`, explicit Nomia decision, and external release evidence.
9. Validate every touched artifact and repository path; package/readiness requires the complete ledger.

## Script Routing

- Intake/state: `scripts/guide_intake.py`, `scripts/governance_contract.py`, `scripts/evaluate_governance.py`.
- Writers/adaptation/projections: `scripts/write_artifact_scaffold.py`, `scripts/write_ops_scaffold.py`, `scripts/adapt_governance.py`, `scripts/project_governance_views.py`, `scripts/project_lifecycle_status.py`, `scripts/normalize_human_artifacts.py`.
- Contracts: `scripts/ecosystem_handoff.py`, `scripts/validate_ecosystem_handoff_contract.py`, `scripts/validate_priority_contract.py`, `scripts/validate_contract_semantics.py`, `scripts/validate_contracts.py`.
- Artifact/path gates: `scripts/validate_artifact.py`, `scripts/validate_board_paths.py`, `scripts/validate_ops.py`, `scripts/validate_roadmap.py`, `scripts/validate_reporting.py`, `scripts/validate_portfolio.py`, `scripts/validate_human_artifacts.py`.
- Scenario/package/release: `scripts/validate_activation_scenarios.py`, `scripts/validate_governance_scenarios.py`, `scripts/validate_golden_examples.py`, `scripts/validate_identity_contract.py`, `scripts/validate_contract_preservation.py`, `scripts/validate_projection_metadata.py`, `scripts/validate_assurance_contract.py`, `scripts/validate_skill_package.py`, `scripts/validate_all.py`, `scripts/package_skill.py`, and `scripts/validate_ecosystem_release.py`.

## Output Contract

Return structured Markdown with profile/stage/mode; roots/identities/provenance; artifacts and canonical/projection authority; volatile evidence source/time/freshness/authority/conflicts/unknowns; separate state dimensions; projection metadata; exact validations/results; untouched outside-scope files; downstream owner/action; and blockers. For readiness/package work, distinguish structural from measured behavior, include scenario categories, package hash/attestation when produced, and never claim live activation, technical completion, validation, or release without corresponding evidence.

## Acceptance Gates

Require one profile/stage/mode; resolved canonical identity for writes; provenance and non-invention; schema v2; attributed non-null technical/release states; strict current v3 handoffs and exact compatible versions; privacy metadata/minimization; no writes to another owner; script-backed templates and atomic writes; explicit non-authoritative projections; preserved unknowns; specialized/path/scenario/golden/identity/priority/contract/preservation/unit/package gates; and deterministic archive free of symlinks, traversal, caches, generated reports, secrets, temporary files, and old zips.

## Stop Conditions

Stop rather than write when roots/IDs/provenance are missing or conflicting; evidence is stale/conflicting; authority is absent; technical/release state lacks attribution; projection source/time cannot be established; work belongs to Mago/Magia; the path is non-canonical; a template script would be bypassed; adaptation would overwrite source or infer technical truth; external sharing violates privacy metadata; or validation fails outside Nomia-owned scope.

## Owned Artifact Families

Board: portfolio, roadmap, governance RFC/decisions, feature map, release/internal notes. Spec: ops, status, stakeholder brief, replanning, feature report. Canonical names/paths are in `references/canonical-paths.md` and `references/contracts.md`.
