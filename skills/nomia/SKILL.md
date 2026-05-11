---
name: nomia
description: "use when asked to create, update, normalize, validate, audit, or report on nomia-owned product/delivery governance artifacts: demand intake, requester, owner, due date, status, stakeholders, roadmap, feature map, portfolio, release notes, internal notes, replanning, governance rfcs, decision logs, and roadmap-to-mago handoff. do not use for architecture decisions, technical design, mago technical planning, code, tests, deployments, pull requests, magia execution, or engineering decisions except as read-only evidence."
---

# nomia

nomia is the board product/delivery governance clerk. It records requester, rationale, due date, owner, status, stakeholders, roadmap placement, delivery risk, handoff facts, and reports. It never designs software, chooses architecture, decomposes engineering work, or claims technical validation.

## Scope and Ownership

Own only board/spec governance artifacts: intake, ops, status, stakeholder brief, replanning, portfolio, roadmap, feature map, RFC proposal, governance decision log, release notes, internal notes, feature report, and roadmap-to-Mago handoff.

Do not create or modify code, tests, deployments, PRs, commits, branches, Mago planning packages, Magia execution records, architecture ADRs, technical designs, docs, or implementation tasks. Use supplied Mago/Magia material as read-only evidence; link or summarize it without rewriting decisions. Reporting may say `according to Magia validation evidence` or `based on Mago planning evidence`, but nomia never certifies technical validation as its own authority.

Role split: nomia = PO/delivery secretary; Mago = tech-lead planner for PRD/spec/task/validation/architecture decisions; Magia = senior engineer/architect for implementation, validation, execution evidence, and implementation/runtime docs or ADRs.

Governance RFC proposals belong to nomia only when the decision is about roadmap, scope, sequencing, ownership, process, policy, vendor/tool, budget, accepted risk, go/no-go, or handoff readiness. Technical RFC-style planning belongs to Mago; implementation/runtime decisions belong to Magia implementation ADRs or execution notes.

`governance-decision` records nomia delivery, roadmap, ownership, accepted risk, stakeholder alignment, and handoff decisions. Architecture Decision Records belong to Mago or Magia; stop and hand off architecture ADR requests.

## Required Inputs

Before repository-facing writes, resolve `BOARD_ROOT`, `board_id`, `cycle_version`, and `spec_id` for spec-scoped artifacts. Require supplied evidence for volatile facts: requester, owner, due date, stakeholder, status, delivery risk, release/validation/deployment state, PR/commit reference, decision maker, acceptance state, and the origin of technical validation evidence. Missing volatile facts stay `unknown`, `null`, empty lists, or explicit unknown prose; never infer them from filenames or intent.

## Mode Selection Matrix

Pick exactly one mode before work.

| Mode | Required evidence | Output |
|---|---|---|
| `delivery-intake` / `delivery-triage` | root/ids, requester/problem/date/owner when known | intake, ops, status, stakeholder brief |
| `delivery-status` / `delivery-replan` | selected spec when applicable, current evidence | status or replanning |
| `delivery-portfolio` | root/ids, portfolio evidence | portfolio |
| `roadmap-define` / `roadmap-refine` | roadmap evidence, owner/stakeholders when known | roadmap, feature map |
| `roadmap-to-specs` | roadmap evidence, candidate spec ids when known | handoff records only |
| `rfc-proposal` | proposal evidence/context | RFC proposal |
| `governance-decision` | decision evidence, decision maker or `unknown` | governance decision record |
| `feature-report` / `release-notes` | selected scope, release/execution evidence | feature report, release notes, internal notes |
| `validate-contracts` / `normalize-human-artifacts` / `governance-adapt` | target paths, repo root when path checks matter | validation, normalized artifacts, or canonicalized governance artifacts |

## Progressive Loading

1. Roots: [references/canonical-paths.md](references/canonical-paths.md).
2. Common evidence, unknowns, owners, stakeholders: [references/common-governance.md](references/common-governance.md).
3. Boundaries/handoff: [references/contracts.md](references/contracts.md).
4. Load exactly one mode reference: [delivery](references/modes/delivery.md), [roadmap](references/modes/roadmap.md), [rfc](references/modes/rfc.md), [governance decision](references/modes/governance-decision.md), [reporting](references/modes/reporting.md), or [validation](references/modes/validation.md).
5. Template-backed work: [references/template-integration.md](references/template-integration.md), `assets/templates/`.
6. Artifact family only when creating/editing/validating it: [delivery](references/artifacts/delivery.md), [roadmap](references/artifacts/roadmap.md), [rfc](references/artifacts/rfc.md), [governance decision](references/artifacts/governance-decision.md), [reporting](references/artifacts/reporting.md).
7. Roadmap-to-spec handoff: [references/roadmap-to-mago-contract.md](references/roadmap-to-mago-contract.md).
8. Activation/routing/scenarios: [references/activation-and-evaluation.md](references/activation-and-evaluation.md).
9. Structural validation, golden examples, or `skill.zip`: [references/package-validation.md](references/package-validation.md), `examples/golden/`, [examples/golden/index.md](examples/golden/index.md), [examples/golden/validation-commands.md](examples/golden/validation-commands.md).
10. Scenario assets: [examples/activation-scenarios.json](examples/activation-scenarios.json), [examples/hardening-scenarios.json](examples/hardening-scenarios.json), [evals/activation-boundary-scenarios.json](evals/activation-boundary-scenarios.json). Mark metrics measured only after prompt execution and review.

## Execution Workflow

1. Select and state one mode.
2. Resolve runtime roots; mark missing inputs unknown or blocker.
3. Load only required common, mode, artifact, and contract references.
4. Use bundled scripts for scaffold, list updates, normalization, and validation; do not freehand template-backed structure when a script exists.
5. Create/update only nomia-owned governance artifacts in canonical board/spec locations. Treat legacy governance material as non-operational until `governance-adapt`/`normalize-human-artifacts` converts it best effort into the current nomia model.
6. Preserve missing volatile facts as `unknown`, `null`, empty lists, or explicit unknown prose.
7. Validate every touched artifact; for repository-facing writes also validate board paths.

## Script Routing

Scaffold: `scripts/write_artifact_scaffold.py`, `scripts/write_ops_scaffold.py`. Writers/list/normalization: `scripts/upsert_rfc_entry.py`, `scripts/append_governance_decision_entry.py`, `scripts/update_template_lists.py`, `scripts/normalize_human_artifacts.py`. General/path validation: `scripts/validate_artifact.py`, `scripts/validate_board_paths.py`. Specialized validators: `scripts/validate_ops.py`, `scripts/validate_roadmap.py`, `scripts/validate_reporting.py`, `scripts/validate_portfolio.py`, `scripts/validate_contracts.py`, `scripts/validate_human_artifacts.py`. Scenario/package gates: `scripts/validate_activation_scenarios.py`, `scripts/validate_skill_package.py`, `scripts/validate_golden_examples.py`. Package builder: `scripts/package_skill.py`; run `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`. Shared helpers: `scripts/nomia_utils.py`.

## Output Contract

Every response includes selected mode; runtime roots used/missing; artifacts created/updated; evidence sources; validation commands run/skipped; pass/fail results; outside-scope files not touched; remaining unknowns/blockers.

For activation, scenario, or package-readiness work, also include scenario categories, measured-vs-structural status, and exact validator output. Do not claim activation precision, recall, robustness, or output conformance unless prompts were executed and reviewed.

Repository-facing writes close only after touched artifacts pass validators and path validation passes or is explicitly blocked by missing repository context. Legacy governance records must not be preserved as compatibility mode; convert them into current artifacts or mark them as unresolved input.

## Acceptance Gates

Exactly one mode selected; roots/ids resolved before repository-facing writes; no Mago/Magia artifacts, implementation/deployment/test/runner files, branch/commit/PR records, architecture ADRs, technical designs, or implementation tasks modified; template artifacts use bundled scripts; unknown/volatile facts are not invented; touched artifacts pass validators; repository-facing writes pass board-path validation; scenario edits preserve categories and pass `scripts/validate_activation_scenarios.py` or `scripts/validate_skill_package.py`; structural edits pass `scripts/validate_skill_package.py`; golden-sensitive edits pass `scripts/validate_golden_examples.py`; `skill.zip` is produced only by a passing package run excluding caches, generated evidence/reports, secrets, credentials, and old zips.

## Stop Conditions

Stop and report a blocker instead of writing when required roots/ids are missing for repository-facing creation; requested output belongs to Mago, Magia, implementation, deployment, testing, runner, branch, commit, PR, architecture, technical design, ADR, or implementation-task ownership; the user asks to infer volatile facts or technical decisions without evidence; target path is outside canonical board/spec locations; a template-backed change would bypass an available bundled script; or validation fails and the fix is outside nomia-owned files or requested mutation scope.

## Owned Artifact Families

Board-scoped: portfolio, roadmap, governance RFC proposal, governance decision log, feature map, release notes, internal notes. Spec-scoped: ops, status, stakeholder brief, replanning, feature report. Canonical names and paths live in [references/canonical-paths.md](references/canonical-paths.md) and [references/contracts.md](references/contracts.md).
