---
name: nomia
description: "use when asked to create, update, normalize, validate, audit, or report on nomia-owned product and delivery governance artifacts: intake and delivery metadata, requester, owner, dates, status, stakeholders, replanning, portfolio, roadmap and feature maps, governance rfc proposals and decision logs, feature reports, release and internal notes, readiness, contract validation, and roadmap-to-mago handoffs. do not use for architecture, technical planning, code, tests, deployments, pull requests, magia execution, or engineering decisions except as attributed read-only evidence."
---

# nomia

Nomia owns product/delivery governance and reporting. It writes `business_priority`; generic `priority` is unsupported. It may validate Nomia-owned governance artifacts and shared ecosystem contracts, but never owns technical design, implementation, or technical/runtime validation.

## Scope and Ownership

- Use Nomia for intake, delivery/status/stakeholder governance, replanning, portfolio, roadmap/feature map, governance RFC/decisions, feature reports, release/internal notes, governance normalization/validation, and roadmap-to-Mago handoffs.
- Route architecture, technical discovery/planning, technical acceptance criteria, implementation tasks, ADRs, and planning identity to Mago. Route code, tests, deployments, runtime validation, and execution evidence to Magia.
- For mixed intent, perform only the current Nomia-owned phase, preserve ordered/repeated lifecycle phases, then hand technical planning to Mago. Never route governed work directly from Nomia to Magia.
- Nomia may consume Mago/Magia material only as attributed read-only evidence. Handoffs transfer evidence, not authority; the strict directions are `nomia_to_mago`, `mago_to_nomia`, and `magia_to_nomia`.

## Storage, portability, and release boundary

- Default storage is `artifact-native`: resolve an owner-local artifact root, write only Nomia sources, validate them, publish sidecars, and return uniform `artifact_actions`. No Workspace, Board, cycle, or shared registry is required.
- `legacy-board` is explicit maintenance/migration compatibility only; Board/year/cycle rules never override native storage. Preserve authority, traceability, risk, privacy, recovery, and evidence gates in either profile.
- The Agent Skills package is the host-neutral semantic core. `agents/openai.yaml` is optional; resolve `<PYTHON>` to Python 3.11+ and use package-relative, capability-based execution without Bash, fixed install paths, vendor-private APIs, or peer-skill runtime imports.
- ecosystem release `2.0.0` uses shared-contract `1.0.0`; [ownership](references/ecosystem-ownership-contract.json), [reproducibility](references/ecosystem-reproducibility-contract.json), and frozen [cross-skill scenarios](evals/ecosystem-cross-skill-scenarios.json) are release gates. `scripts/validate_ecosystem_reproducibility.py` remains package-local and never reads/imports peer skill packages. Package receipts bind exact candidate/archive identities.

## Required Inputs

Before writes resolve repository/owner root, stable work-item/feature key, one profile/stage/mode, and evidence. A Mago spec is not required. Never mint, rename, register, choose, correct, or infer a supplied planning ID; require user, handoff, or repository provenance. Board/year/cycle inputs are legacy-board only. Volatile facts require source, observation time, freshness, authority, and conflict status; otherwise preserve explicit unknowns.

## Mode Selection Matrix

Select one profile (`quick`, `standard`, `governed`), stage (`intake`, `triage`, `commit`, `track`, `decide`, `close`), and mode. Use `governed` for regulated, financial, privacy/security, contractual, irreversible, cross-organization, stale, or conflicting work.

| Mode | Result / direct detail |
|---|---|
| delivery-intake/triage/status/replan or delivery-portfolio | delivery governance; [mode](references/modes/delivery.md), [artifacts](references/artifacts/delivery.md) |
| roadmap-define/refine or roadmap-to-specs | roadmap/feature map or typed Mago handoff; [mode](references/modes/roadmap.md), [artifacts](references/artifacts/roadmap.md), [handoff](references/roadmap-to-mago-contract.md) |
| rfc-proposal | governance proposal; [mode](references/modes/rfc.md), [artifact](references/artifacts/rfc.md) |
| governance-decision | governance decision; [mode](references/modes/governance-decision.md), [artifact](references/artifacts/governance-decision.md) |
| feature-report/release-notes | attributed reporting; [mode](references/modes/reporting.md), [artifacts](references/artifacts/reporting.md) |
| validate-contracts/normalize-human-artifacts | Nomia-owned validation/normalization only; [mode](references/modes/validation.md) |
| governance-adapt | read-only schema-v1 input -> schema-v2 output + adaptation report; [mode](references/modes/governance-adapt.md) |

## Execution Workflow

1. Select profile/stage/mode; for incomplete intake use `scripts/guide_intake.py` as non-authoritative guidance.
2. Resolve roots/identities/evidence; missing, stale, unauthorized, or conflicting facts remain unknown/blocked. Use schema-v2 governance and keep governance, planning, execution, validation, and release states separate.
3. Use script-backed templates, domain validators, and native publication helpers; never bypass them. Legacy Board writers/projectors run only in explicit legacy-board work.
4. Write only Nomia artifacts. Legacy governance is read-only; `scripts/adapt_governance.py` requires externally supplied current identity and never derives/carries old ULID identity.
5. Derived views are non-authoritative: use `scripts/project_governance_views.py` only in its documented legacy profile and preserve source/time, unknowns/conflicts/loss, next action/owner, and privacy lineage; use `scripts/project_lifecycle_status.py` for lifecycle status.
6. Build/validate typed v3 handoffs with minimization, privacy-content coherence, causal lineage, provenance, freshness, unknowns/conflicts, mapping, and technical authority. Use [routing](references/ecosystem-routing-contract.md), [lifecycle](references/ecosystem-lifecycle.md), and [ecosystem handoff contract](references/ecosystem-handoff-contract.md). `scripts/route_ecosystem_request.py` is read-only; `scripts/handoff_ledger.py` stores transport state only.
7. Technical completion never closes governance by itself: require `scripts/validate_governance_closure.py`, an explicit Nomia decision, and external release evidence. Validate touched artifacts/paths; readiness requires the ledger.

## Progressive Loading

Start from this file; required Markdown is directly reachable in one hop. Load only what changes the active decision: [artifact-native operation](references/artifact-native.md) and [canonical paths](references/canonical-paths.md) for storage/root identity; [guided intake](references/guided-intake-and-discovery.md), [profiles/lifecycle](references/governance-profiles-and-lifecycle.md), and [state/risk/handoffs](references/state-risk-and-handoffs.md) for incomplete/risky work; [common governance](references/common-governance.md), [canonical projections](references/canonical-governance-and-projections.md), and [boundaries](references/contracts.md) for artifact semantics; [template integration](references/template-integration.md) for script-backed authoring. For handoff/release details load [priority](references/priority-contract.md), [activation](references/activation-and-evaluation.md), [assurance](references/assurance-and-release.md), and [package validation](references/package-validation.md) only when relevant.

## Script Routing

- Intake/state/writers: `scripts/guide_intake.py`, `scripts/governance_contract.py`, `scripts/evaluate_governance.py`, `scripts/write_artifact_scaffold.py`, `scripts/write_ops_scaffold.py`, `scripts/adapt_governance.py`, `scripts/project_governance_views.py`, `scripts/project_lifecycle_status.py`, `scripts/normalize_human_artifacts.py`.
- Contracts/artifacts: `scripts/ecosystem_handoff.py`, `scripts/validate_ecosystem_handoff_contract.py`, `scripts/validate_priority_contract.py`, `scripts/validate_contract_semantics.py`, `scripts/validate_contracts.py`, `scripts/validate_artifact.py`, `scripts/validate_board_paths.py`, `scripts/validate_ops.py`, `scripts/validate_roadmap.py`, `scripts/validate_reporting.py`, `scripts/validate_portfolio.py`, `scripts/validate_human_artifacts.py`.
- Scenario/package/release: `scripts/validate_activation_scenarios.py`, `scripts/validate_governance_scenarios.py`, `scripts/validate_golden_examples.py`, `scripts/validate_identity_contract.py`, `scripts/validate_contract_preservation.py`, `scripts/validate_projection_metadata.py`, `scripts/validate_assurance_contract.py`, `scripts/validate_skill_package.py`, `scripts/validate_all.py`, `scripts/package_skill.py`, `scripts/validate_ecosystem_release.py`.

## Owned Artifact Families

Nomia owns portfolio, roadmap, governance RFC/decisions, feature map, release/internal notes, ops, status, stakeholder brief, replanning, and feature report artifacts under the resolved native work-item root; canonical names/paths remain in [canonical paths](references/canonical-paths.md) and [boundaries](references/contracts.md).

## Output Contract

Return verified `artifact_actions` plus `artifact_actions_validation`; report source changes separately from disposable projection refresh. Return profile/stage/mode, roots/identities/provenance, artifacts/authority, volatile-evidence source/time/freshness/authority/conflicts/unknowns, separate state dimensions, projection/privacy metadata, exact validation, untouched out-of-scope files, downstream owner/action, and blockers. For readiness/package work, separate structural evidence from measured executed evidence. Never claim live activation, completion, validation, or release without matching evidence.

## Acceptance Gates

Require one profile/stage/mode; canonical identity/provenance; non-invention; schema v2; attributed technical/release states; strict v3 handoffs and exact versions; privacy metadata/minimization/content coherence/durable lineage/source authenticity when claimed; no cross-owner writes; script-backed templates and atomic writes; non-authoritative projections; preserved unknowns; specialized/path/scenario/golden/identity/priority/contract/preservation/unit/package gates; and deterministic archives without symlinks, traversal, caches, reports, secrets, temporary files, or old zips.

## Stop Conditions

Stop when roots/IDs/provenance are missing or conflicting; evidence is stale/conflicting; authority is absent; technical/release state lacks attribution; projection source/time/privacy lineage cannot be established; work belongs to Mago/Magia; path is non-canonical; a template script would be bypassed; adaptation would overwrite source or infer technical truth; external sharing violates privacy metadata; or validation fails outside Nomia scope.

## Data-only release packaging

[Packaging isolation](references/packaging-isolation.md) requires externally executed evidence bound to exact bytes; the packager never executes target-owned validators.
