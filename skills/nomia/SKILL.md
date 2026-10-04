---
name: nomia
description: "use when asked to create, update, normalize, validate, audit, or report on nomia-owned product and delivery governance artifacts: intake and delivery metadata, requester, owner, dates, status, stakeholders, replanning, portfolio, roadmap and feature maps, governance rfc proposals and decision logs, feature reports, release and internal notes, readiness, contract validation, and roadmap-to-mago handoffs. do not use for architecture, technical planning, code, tests, deployments, pull requests, magia execution, or engineering decisions except as attributed read-only evidence."
---

# nomia

Nomia owns product/delivery governance and reporting. It never owns technical design or technical/runtime validation; it may validate Nomia-owned governance artifacts and ecosystem contracts. It writes `business_priority`; generic `priority` is unsupported.


## Default storage and artifact orchestration

Use [artifact-native operation](references/artifact-native.md) before all storage-specific guidance. Each domain decides its own files, writes only its own sources, validates content, publishes sidecars and returns uniform `artifact_actions`. No Workspace, Board, cycle or shared registry is required. Retained Board-specific commands/examples apply only to explicitly selected `legacy-board` maintenance/migration; their storage mechanics never override the native default. Preserve all domain authority, traceability, risk, privacy, recovery and evidence gates.


## Portability

The Agent Skills package is the host-neutral semantic core. `agents/openai.yaml` is an optional OpenAI adapter and must not be required for correctness. Resolve `<PYTHON>` to an available Python 3.11+ launcher; use package-relative paths and capability-based execution; do not depend on Bash, fixed install paths, or vendor-private APIs for core behavior.

## Coordinated reproducibility contract

This package participates in ecosystem release `2.0.0` with shared-contract version `1.0.0`. Use [ecosystem ownership](references/ecosystem-ownership-contract.json), [reproducibility](references/ecosystem-reproducibility-contract.json), and the frozen [cross-skill scenarios](evals/ecosystem-cross-skill-scenarios.json) as release gates. `scripts/validate_ecosystem_reproducibility.py` is package-local; it must not read/import peer skill packages. Package receipts bind baseline, frozen candidate, shared-contract, and archive hashes; the coordinator may combine those receipts into ecosystem compatibility evidence without creating runtime coupling.

## Distributed ecosystem routing

Use the [routing contract](references/ecosystem-routing-contract.md) and [lifecycle](references/ecosystem-lifecycle.md). Perform only the current governance phase, preserve repeats, then route planning to Mago; never route governed work directly to Magia. `scripts/route_ecosystem_request.py` is read-only; `scripts/handoff_ledger.py` stores transport state only.

## Scope and Ownership

- Own: intake, ops/status/stakeholder brief, replanning, portfolio, roadmap/feature map, governance RFC/decisions, release/internal notes, feature report, and roadmap-to-Mago handoff.
- Never change code, tests, deployments, source control, Mago planning, Magia execution, ADR/technical design, implementation tasks/docs, or technical validation. Consume technical material read-only with attribution.
- Mago owns technical spec identity and planning (cycle identity only in legacy-board compatibility); Magia owns implementation/validation evidence. Nomia does not require Mago or Magia skill files at runtime.
- Use the strict [ecosystem handoff contract](references/ecosystem-handoff-contract.md) through `scripts/ecosystem_handoff.py`: produce `nomia_to_mago`; consume `mago_to_nomia` and `magia_to_nomia`. Handoffs transfer evidence only.
- Governance decides business concerns; technical decisions are handed off.

## Required Inputs

Before writes resolve the repository/owner root, stable work-item/feature key, profile/stage/mode and evidence. Governance does not require a Mago spec to exist. If a planning ID is supplied, Nomia must not mint, rename/register or infer it; require user, handoff or repository provenance. Board/year/cycle inputs are confined to explicitly selected legacy-board adapters.

Volatile facts require source, observation time, freshness, authority, and no conflict; otherwise preserve explicit unknowns.

## Mode Selection Matrix

Select one profile (`quick`, `standard`, `governed`), stage (`intake`, `triage`, `commit`, `track`, `decide`, `close`), and mode. Use `governed` for regulated, financial, privacy/security, contractual, irreversible, cross-organization, stale, or conflicting work.

| Mode | Output |
|---|---|
| delivery-intake/triage/status/replan | intake, ops, status, stakeholder brief, replanning |
| delivery-portfolio | portfolio |
| roadmap-define/refine | roadmap and feature map |
| roadmap-to-specs | typed Mago handoff only; existing/evidenced candidate IDs optional |
| rfc-proposal/governance-decision | governance proposal/decision |
| feature-report/release-notes | attributed reports/notes |
| validate-contracts/normalize-human-artifacts | validation/normalization |
| governance-adapt | schema-v2 output plus adaptation report from read-only schema-v1 input |

## Progressive Loading

1. Load [canonical paths](references/canonical-paths.md), [common governance](references/common-governance.md), [guided intake](references/guided-intake-and-discovery.md), [profiles/lifecycle](references/governance-profiles-and-lifecycle.md), [state/risk/handoffs](references/state-risk-and-handoffs.md), [canonical projections](references/canonical-governance-and-projections.md), then [boundaries](references/contracts.md).
2. Load exactly one mode: [delivery](references/modes/delivery.md), [roadmap](references/modes/roadmap.md), [RFC](references/modes/rfc.md), [decision](references/modes/governance-decision.md), [reporting](references/modes/reporting.md), [validation](references/modes/validation.md), or [adapt](references/modes/governance-adapt.md).
3. Load [template integration](references/template-integration.md) and only the affected artifact family: [delivery](references/artifacts/delivery.md), [roadmap](references/artifacts/roadmap.md), [RFC](references/artifacts/rfc.md), [decision](references/artifacts/governance-decision.md), [reporting](references/artifacts/reporting.md).
4. For handoff/release load [roadmap-to-Mago](references/roadmap-to-mago-contract.md), [priority](references/priority-contract.md), [activation](references/activation-and-evaluation.md), [assurance](references/assurance-and-release.md), and [package validation](references/package-validation.md) only when relevant.

## Execution Workflow

1. Select profile/stage/mode. For incomplete intake use `scripts/guide_intake.py`; guidance is non-authoritative.
2. Resolve roots/identities/evidence; mark missing, stale, or conflicting facts unknown/blocked.
3. Use schema-v2 governance records; keep governance, planning, execution, validation, and release states separate.
4. Use domain content validators and native publication helpers; never bypass script-backed governance semantics. Board scaffold/projector entrypoints apply only to the legacy-board profile.
5. Write only Nomia artifacts. Legacy governance is read-only; `scripts/adapt_governance.py` requires externally supplied current identity and never derives/carries old ULID identity.
6. When a domain-specific non-authoritative view is requested, use `scripts/project_governance_views.py` in its documented legacy profile, preserving canonical source, generated/evidence timestamps, unknowns/conflicts/loss, next action, owner, and privacy lineage. Use `scripts/project_lifecycle_status.py` for lifecycle status.
7. Build/validate typed v3 handoffs with minimization, content/metadata privacy coherence, causal lineage, provenance, freshness, unknowns, conflicts, mapping, and technical authority.
8. Technical completion cannot close governance without `scripts/validate_governance_closure.py`, explicit Nomia decision, and external release evidence.
9. Validate touched artifacts/paths; readiness requires the ledger.

## Script Routing

- Intake/state: `scripts/guide_intake.py`, `scripts/governance_contract.py`, `scripts/evaluate_governance.py`.
- Writers/adaptation/projections: `scripts/write_artifact_scaffold.py`, `scripts/write_ops_scaffold.py`, `scripts/adapt_governance.py`, `scripts/project_governance_views.py`, `scripts/project_lifecycle_status.py`, `scripts/normalize_human_artifacts.py`.
- Contracts: `scripts/ecosystem_handoff.py`, `scripts/validate_ecosystem_handoff_contract.py`, `scripts/validate_priority_contract.py`, `scripts/validate_contract_semantics.py`, `scripts/validate_contracts.py`.
- Artifact/path gates: `scripts/validate_artifact.py`, `scripts/validate_board_paths.py`, `scripts/validate_ops.py`, `scripts/validate_roadmap.py`, `scripts/validate_reporting.py`, `scripts/validate_portfolio.py`, `scripts/validate_human_artifacts.py`.
- Scenario/package/release: `scripts/validate_activation_scenarios.py`, `scripts/validate_governance_scenarios.py`, `scripts/validate_golden_examples.py`, `scripts/validate_identity_contract.py`, `scripts/validate_contract_preservation.py`, `scripts/validate_projection_metadata.py`, `scripts/validate_assurance_contract.py`, `scripts/validate_skill_package.py`, `scripts/validate_all.py`, `scripts/package_skill.py`, `scripts/validate_ecosystem_release.py`.

## Output Contract

Include the verified uniform `artifact_actions` array and `artifact_actions_validation` from native publication; report source changes separately from disposable projection refresh.

Return structured Markdown with profile/stage/mode; roots/identities/provenance; artifacts and authority; volatile evidence source/time/freshness/authority/conflicts/unknowns; separate state dimensions; projection/privacy metadata; exact validation; untouched outside-scope files; downstream owner/action; blockers. For readiness/package work separate structural and measured evidence; never claim live activation, completion, validation, or release without proof.

## Acceptance Gates

Require one profile/stage/mode; canonical identity/provenance; non-invention; schema v2; attributed technical/release states; strict v3 handoffs and exact versions; privacy metadata, minimization, content coherence, declared durable lineage, and verified source-handoff authenticity when claimed; no cross-owner writes; script-backed templates and atomic writes; non-authoritative projections; preserved unknowns; specialized/path/scenario/golden/identity/priority/contract/preservation/unit/package gates; and deterministic archives without symlinks, traversal, caches, reports, secrets, temporary files, or old zips.

## Stop Conditions

Stop when roots/IDs/provenance are missing/conflicting; evidence is stale/conflicting; authority is absent; technical/release state lacks attribution; projection source/time/privacy lineage cannot be established; work belongs to Mago/Magia; path is non-canonical; a template script would be bypassed; adaptation would overwrite source or infer technical truth; external sharing violates privacy metadata; or validation fails outside Nomia scope.

## Owned Artifact Families

Native governance root: portfolio, roadmap, governance RFC/decisions, feature map, release/internal notes, ops, status, stakeholder brief, replanning and feature report. Subdirectories follow the work item; no shared Board is required. Canonical names/paths are in [canonical paths](references/canonical-paths.md) and [contracts](references/contracts.md).

## Data-only release packaging

[Packaging isolation](references/packaging-isolation.md) requires externally executed evidence bound to exact bytes; no target-owned validator is executed by the packager.
