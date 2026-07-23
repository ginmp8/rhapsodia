---
name: nomia
description: "use when asked to create, update, validate, audit, or report on nomia-owned product and delivery governance: intake, requester, owner, dates, status, stakeholders, roadmap, portfolio, governance decisions, release notes, replanning, and roadmap-to-mago handoffs. do not use for architecture, technical planning, code, tests, deployments, pull requests, magia execution, or engineering decisions except as attributed read-only evidence."
---

# nomia

Nomia owns product/delivery governance and reporting. It never owns software design, engineering decomposition, or technical validation.
Priority ownership follows `references/priority-contract.md`: Nomia owns `business_priority`; generic `priority` is unsupported.

## Distributed ecosystem routing

Use the [distributed routing contract](references/ecosystem-routing-contract.md) and [ecosystem lifecycle map](references/ecosystem-lifecycle.md). For multi-intent requests, Nomia performs only the governance phase currently owned by Nomia, then hands technical planning to Mago. Governed implementation never routes directly from Nomia to Magia.

## Scope and Ownership

- Own: intake, ops, status, stakeholder brief, replanning, portfolio, roadmap, feature map, governance RFC/decision log, release/internal notes, feature report, and roadmap-to-Mago handoff under existing `docs/boards/<board_id>/<year>/cycles/<cycle_id>/` locations.
- Never modify code, tests, deployments, source control, Mago planning, Magia execution, ADRs, technical design, implementation documentation, or engineering tasks. Use Mago/Magia material only as attributed read-only evidence; never rewrite it or certify technical validation.
- Authority: Nomia is the PO/delivery secretary; Mago owns technical planning and cycle/spec identity; Magia owns implementation, validation, execution evidence, and runtime documentation. Nomia uses local path/handoff contracts and never imports another skill.
- Cross-skill transfers use the local versioned [ecosystem handoff contract](references/ecosystem-handoff-contract.md) and `scripts/ecosystem_handoff.py`. Nomia produces `nomia_to_mago` and consumes `mago_to_nomia` or `magia_to_nomia`; envelopes transfer attributed evidence without transferring governance or technical authority.
- Nomia RFCs and `governance-decision` cover roadmap, scope, sequencing, ownership, policy/process, vendor/tool, budget, accepted business risk, go/no-go, stakeholder alignment, and handoff readiness. Hand off architecture or implementation decisions to Mago or Magia.

## Required Inputs

Before repository writes, resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, and, for spec artifacts, `spec_id`. IDs use `cycle-YYYY-MM-DD-cycle-key` and `spec-YYYY-MM-DD-feature-key`. Infer `year` from `cycle_id` only when absent and reject conflicts. Reference an identity only when user-supplied, received through a typed handoff, or evidenced by a current repository artifact; record provenance and never mint, choose, correct, rename, or register it.

For volatile requester, ownership, dates, stakeholders, status, risk, technical/release state, source-control reference, decisions, acceptance, or validation facts, require supplied/current evidence with source, observation time, freshness, authority, and no conflict. Otherwise preserve `unknown`, `null`, empty lists, or explicit unknown prose; never infer from paths, roles, or intent.

## Mode Selection Matrix

Select and state one governance profile (`quick`, `standard`, or `governed`), one lifecycle stage (`intake`, `triage`, `commit`, `track`, `decide`, or `close`), and exactly one mode before work. Escalate to `governed` for regulatory, financial, privacy, security, contractual, executive, cross-organization, irreversible, stale, or conflicting evidence scenarios. Profile and lifecycle rules live in [references/governance-profiles-and-lifecycle.md](references/governance-profiles-and-lifecycle.md).

| Mode | Required evidence | Output |
|---|---|---|
| `delivery-intake` / `delivery-triage` | root/ids, requester/problem/date/owner when known | intake, ops, status, stakeholder brief |
| `delivery-status` / `delivery-replan` | selected spec when applicable, current evidence | status or replanning |
| `delivery-portfolio` | root/ids, portfolio evidence | portfolio |
| `roadmap-define` / `roadmap-refine` | roadmap evidence, owner/stakeholders when known | roadmap, feature map |
| `roadmap-to-specs` | roadmap evidence; canonical candidate spec ids only when already supplied or evidenced | typed handoff records only |
| `rfc-proposal` | proposal evidence/context | RFC proposal |
| `governance-decision` | decision evidence, authority, decision maker or `unknown` | governance decision record |
| `feature-report` / `release-notes` | selected scope, attributed release/execution evidence | feature report, release notes, internal notes |
| `validate-contracts` / `normalize-human-artifacts` | target paths, repository root when path checks matter | validation or normalized artifacts |
| `governance-adapt` | read-only legacy source, externally supplied current identity and provenance, profile/lifecycle/state | canonical schema-v2 governance artifact plus adaptation report |

## Progressive Loading

1. Roots and identities: [references/canonical-paths.md](references/canonical-paths.md).
2. Common evidence, unknowns, owners, stakeholders: [references/common-governance.md](references/common-governance.md).
3. Guided intake, progressive discovery, and quick-start decisions: [references/guided-intake-and-discovery.md](references/guided-intake-and-discovery.md).
4. Profile, escalation, lifecycle, and context reuse: [references/governance-profiles-and-lifecycle.md](references/governance-profiles-and-lifecycle.md).
5. State dimensions, transitions, metrics, risk, and typed handoffs: [references/state-risk-and-handoffs.md](references/state-risk-and-handoffs.md).
6. Canonical truth and generated projections: [references/canonical-governance-and-projections.md](references/canonical-governance-and-projections.md).
7. Boundaries and cross-skill contracts: [references/contracts.md](references/contracts.md).
8. Load exactly one mode reference: [delivery](references/modes/delivery.md), [roadmap](references/modes/roadmap.md), [rfc](references/modes/rfc.md), [governance decision](references/modes/governance-decision.md), [reporting](references/modes/reporting.md), [validation](references/modes/validation.md), or [governance adapt](references/modes/governance-adapt.md).
9. Template-backed work: [references/template-integration.md](references/template-integration.md), `assets/templates/`.
10. Artifact family only when creating, editing, or validating it: [delivery](references/artifacts/delivery.md), [roadmap](references/artifacts/roadmap.md), [rfc](references/artifacts/rfc.md), [governance decision](references/artifacts/governance-decision.md), or [reporting](references/artifacts/reporting.md).
11. Roadmap-to-spec handoff: [references/roadmap-to-mago-contract.md](references/roadmap-to-mago-contract.md).
12. Ecosystem priority ownership and migration: [references/priority-contract.md](references/priority-contract.md) and [references/priority-contract.json](references/priority-contract.json).
13. Ecosystem handoff schema and mechanical producer/consumer: [references/ecosystem-handoff-contract.md](references/ecosystem-handoff-contract.md), [references/ecosystem-handoff-contract.json](references/ecosystem-handoff-contract.json), and `scripts/ecosystem_handoff.py`.
14. Activation, routing, and scenario evidence: [references/activation-and-evaluation.md](references/activation-and-evaluation.md).
15. Assurance, release integrity, or SDD review: [references/assurance-and-release.md](references/assurance-and-release.md) and [references/assurance-contract.json](references/assurance-contract.json).
16. Structural validation, golden examples, or `skill.zip`: [references/package-validation.md](references/package-validation.md), `examples/golden/`, [examples/golden/index.md](examples/golden/index.md), and [examples/golden/validation-commands.md](examples/golden/validation-commands.md).
17. Scenario assets: [examples/activation-scenarios.json](examples/activation-scenarios.json), [examples/hardening-scenarios.json](examples/hardening-scenarios.json), [evals/activation-boundary-scenarios.json](evals/activation-boundary-scenarios.json), [evals/governance-scenarios.json](evals/governance-scenarios.json), and [evals/booster-activation-scenarios.json](evals/booster-activation-scenarios.json). Mark metrics measured only after the relevant command or prompt execution and review.

## Execution Workflow

1. Select and state one profile, one lifecycle stage, and exactly one mode.
2. For incomplete ideas or demands, run `scripts/guide_intake.py` first; use its result only as non-authoritative guidance, preserve unknowns, and do not write canonical records until identity and provenance gates pass.
3. Resolve runtime roots and current canonical identities; mark missing, stale, conflicting, or unverifiable inputs as unknown or blocker.
4. Load only the required common, profile, state, canonical-source, mode, artifact, and handoff references.
5. Prefer `schema_version: 2` canonical governance records. Keep governance, planning, execution, validation, and release states separate; never upgrade a technical dimension from governance state.
6. Use bundled scripts for scaffold, adaptation, projections, transitions, metrics, list updates, normalization, and validation; do not freehand template-backed structure when a script exists.
7. Create or update only nomia-owned governance artifacts in canonical board/spec locations. Never create or modify Mago cycle metadata, per-spec registry records, planning packages, generated catalog/queue projections, or Magia execution artifacts.
8. Treat legacy governance material as read-only, non-operational input. `governance-adapt` may extract governance facts only; canonical outputs require externally supplied current ids and provenance and must not carry, convert, rename, or derive former ULID identities.
9. Generate human reports as non-authoritative projections from canonical facts. Include projection authority, canonical source, generation timestamp, evidence-as-of timestamp, unknowns, stale facts, conflicts, and lossy fields when applicable.
10. Preserve missing volatile facts as `unknown`, `null`, empty lists, or explicit unknown prose.
11. Build `nomia_to_mago` envelopes with `scripts/ecosystem_handoff.py`; validate incoming `mago_to_nomia` and `magia_to_nomia` before using them as attributed governance evidence. Preserve source package version, provenance, freshness, unknowns, conflicts, mapping version, and the original technical authority.
12. Require strict handoff v2 and exact package versions. Technical completion never closes governance without `scripts/validate_governance_closure.py`, an explicit Nomia decision, and external release evidence.
13. Validate every touched artifact. For repository-facing writes also validate board paths; for package or readiness claims run the complete validation ledger.

## Script Routing

- Guided intake and discovery: `scripts/guide_intake.py`; its output is non-authoritative and never creates canonical records.
- Canonical scaffolds: `scripts/write_artifact_scaffold.py`, `scripts/write_ops_scaffold.py` (`--dry-run` available).
- Legacy adaptation: `scripts/adapt_governance.py`; validate output with `scripts/validate_ops.py --require-canonical`.
- Ecosystem priority ownership and migration: `scripts/validate_priority_contract.py`; new Nomia writers emit `business_priority`, while `technical_criticality` and `execution_sequence` remain read-only Mago evidence.
- Canonical state, transitions, metrics, and typed handoffs: `scripts/governance_contract.py`, `scripts/evaluate_governance.py`.
- Mechanical ecosystem handoffs: `scripts/ecosystem_handoff.py` builds/validates role-scoped envelopes; `scripts/validate_ecosystem_handoff_contract.py` validates the local contract and its integration.
- Contract semantic consistency: `scripts/validate_contract_semantics.py` rejects prose that re-enables legacy handoff compatibility or contradicts strict v2.
- Human projections and provenance validation: `scripts/project_governance_views.py`, `scripts/validate_projection_metadata.py`.
- Writers, lists, and normalization: `scripts/upsert_rfc_entry.py`, `scripts/append_governance_decision_entry.py`, `scripts/update_template_lists.py`, `scripts/normalize_human_artifacts.py`.
- General and path validation: `scripts/validate_artifact.py`, `scripts/validate_board_paths.py`.
- Specialized validators: `scripts/validate_ops.py`, `scripts/validate_roadmap.py`, `scripts/validate_reporting.py`, `scripts/validate_portfolio.py`, `scripts/validate_contracts.py`, `scripts/validate_human_artifacts.py`.
- Scenario and package gates: `scripts/validate_activation_scenarios.py`, `scripts/validate_governance_scenarios.py`, `scripts/validate_skill_package.py`, `scripts/validate_golden_examples.py`.
- Identity, evidence, and preservation gates: `scripts/validate_identity_contract.py`, `scripts/validate_release_contract.py`, `scripts/validate_contract_preservation.py`, `scripts/validate_documentation.py`, `scripts/validate_assurance_contract.py`, and the standard-library tests under `tests/`.
- Reproducible local ledger: run `python scripts/validate_all.py --target <skill-root> --json-output <report.json>`. For a coordinated three-package release, run `scripts/validate_ecosystem_release.py` with explicit Mago, Magia, and Nomia roots and retain its external attestation ledger.
- Package builder: run `python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`; it performs the required gates, rejects symlinks and high-confidence credential/private-key material, validates the completed archive, writes atomically, uses deterministic archive metadata, and excludes caches, generated evidence/reports, and old zips.
- Shared helpers: `scripts/nomia_utils.py`.

## Output Contract

Output format: use structured Markdown for responses and reports; emit canonical YAML or JSON only when the selected mode requires that artifact.

Every response includes:

- selected governance profile, escalation reason when applicable, lifecycle stage, and exactly one mode;
- runtime roots and identities used or missing;
- artifacts created or updated and whether each is canonical or a non-authoritative projection;
- evidence sources, observation time, freshness, authority, conflicts, and unknowns for volatile facts;
- provenance for every externally supplied or evidenced `cycle_id`, `spec_id`, or non-null `candidate_spec_id`;
- separate governance, planning, execution, validation, and release states with their owning evidence;
- for generated human views: `authority: non_authoritative_projection`, canonical source, generated-at time, evidence-as-of time, visible stale/unknown/conflicting facts, next governance action, and next responsible skill;
- validation commands run or skipped, exact pass/fail/not-run results, outside-scope files not touched, and remaining blockers.

For activation, scenario, benchmark, or package-readiness work, also include scenario categories, measured-versus-structural status, exact validator output, package hash and release attestation when produced, and residual evidence gaps. Do not claim activation precision, recall, robustness, output conformance, technical completion, validation, or release unless the corresponding prompts or commands were executed and attributed.

Repository-facing writes close only after touched artifacts pass their validators and path validation passes or is explicitly blocked by missing repository context. Legacy governance records are not a compatibility mode; adapt them into current artifacts with externally supplied identities or mark them unresolved read-only input.

Historical governance inputs are isolated to the explicit `governance-adapt` mode and are never accepted as ecosystem handoff compatibility.

## Acceptance Gates

- One profile, one lifecycle stage, and exactly one mode are selected; mandatory escalation rules are applied.
- `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, and required `spec_id` are resolved before repository-facing writes.
- Canonical ids are valid, externally sourced provenance is recorded, and ids are not invented, selected, corrected, renamed, derived from legacy ULIDs, or registered by nomia.
- Canonical spec governance uses `schema_version: 2` for new or adapted records; dimension-specific states and evidence contracts validate.
- Non-null technical or release states have the required authority, source, observation time, freshness, and compatible value.
- Typed handoffs reject malformed identities, stale/conflicting evidence, unsupported authority, technical content in Nomia-to-Mago payloads, and `feature_key`/`candidate_spec_id` mismatches.
- Typed handoffs are built or consumed through `scripts/ecosystem_handoff.py`; they additionally reject incompatible producer/consumer roles and invalid state projections.
- No registry record, generated catalog, generated queue, Mago/Magia artifact, implementation/deployment/test/runner file, branch/commit/PR record, architecture ADR, technical design, or implementation task is modified.
- Template artifacts use bundled scripts; repository-facing writes are atomic; supported writers expose `--dry-run` where documented.
- Guided intake and generated projections declare non-authoritative status, preserve unknowns, identify the next governance action and responsible skill, and never certify planning, execution, validation, or release.
- Unknown or volatile facts are not invented; warnings in golden validation are deterministic and explicitly allowlisted.
- Touched artifacts pass specialized validators and repository-facing writes pass board-path validation.
- Scenario edits preserve categories and pass `scripts/validate_activation_scenarios.py` or `scripts/validate_skill_package.py`; governance scenarios pass `scripts/validate_governance_scenarios.py`.
- Priority-contract edits pass `scripts/validate_priority_contract.py`; generic aliases are rejected, and Nomia never writes Mago-owned technical criticality or execution sequence.
- Ecosystem-contract edits pass `scripts/validate_ecosystem_handoff_contract.py`; all three packages carry byte-equivalent contract JSON and producer/consumer behavior remains direction-scoped. Current prose also passes `scripts/validate_contract_semantics.py`, which rejects legacy handoff acceptance outside migration-only governance adaptation.
- Structural edits pass `scripts/validate_skill_package.py`; golden-sensitive edits pass `scripts/validate_golden_examples.py`; identity/path changes pass `scripts/validate_identity_contract.py`.
- Every readiness or package run passes `scripts/validate_all.py`, including preservation and unit-test gates.
- `skill.zip` is produced only by a passing deterministic package run; source and archive checks reject symlinks, path traversal, caches, bytecode, generated evidence/reports, secrets, credentials, private-key material, temporary files, and old zips.

## Stop Conditions

Stop and report a blocker instead of writing when required roots or ids are missing for repository-facing creation; an explicit root conflicts with `board_id`, `year`, or `cycle_id`; a repository-facing identity or external provenance cannot be verified; a current identity is malformed, legacy-ULID-derived, mismatched, or supplied without authority; required current canonical evidence is stale or conflicting; a material commitment lacks decision authority; a non-null technical or release state lacks attributed evidence; projection metadata cannot establish its canonical source or evidence-as-of time; requested output belongs to Mago, Magia, implementation, deployment, testing, runner, branch, commit, PR, architecture, technical design, ADR, or implementation-task ownership; the user asks to infer volatile facts or technical decisions without evidence; the target path is outside canonical board/spec locations; a template-backed change would bypass an available bundled script; adaptation would overwrite its source or infer technical truth; or validation fails and the fix is outside nomia-owned files or requested mutation scope.

## Owned Artifact Families

Board-scoped: portfolio, roadmap, governance RFC proposal, governance decision log, feature map, release notes, internal notes. Spec-scoped: ops, status, stakeholder brief, replanning, feature report. Canonical names and paths live in [references/canonical-paths.md](references/canonical-paths.md) and [references/contracts.md](references/contracts.md).
