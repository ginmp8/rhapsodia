---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction strategy, refactoring plans, architecture decisions, planned-decision records, execution handoff plans, tasks, validation plans, contract specs, migrations, observability, operations, security/risk notes, discovery, ordering, and define/refine workflows. do not use for execution work, delivery governance/status reporting, stakeholder communication, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Plan intended technical work from Nomia intake and repository evidence. Mago owns planning; it does not modify product code, deploy, commit, open PRs, accept business risk, or own delivery governance. Mago does not fabricate runtime evidence.

## Authority and canonical state

- Nomia owns requester, owner, due date, priority, stakeholders, roadmap, status, release notes, and governance decisions.
- Mago owns intended requirements, design, decisions, tasks, validation plans, technical risks, and execution handoff.
- Implementation and runtime evidence belong exclusively to Magia. Mago may read Magia evidence only for reconciliation and must not rewrite it.
- A Mago planning boundary is an authoring boundary, not an execution prohibition: execution-required tasks are valid planning outputs when bounded, evidenced, assigned to downstream Magia, and paired with a validation path. Mago never performs those tasks.

Write only under a resolved `BOARD_ROOT` using [canonical paths](references/canonical-paths.md) and [concurrent identity/registry rules](references/concurrent-planning.md). Immutable cycle/spec identity and registry state are authoritative; generated catalogs, queues, deltas, adapters, traceability matrices, and reconciliation reports are non-authoritative deterministic projections. Never create parallel trees, mutable sequence counters, duplicate `feature_key` records, or manually edited generated views.

Use [shared ownership](references/shared-artifact-ownership.md) whenever Mago and Magia touch the same package. Legacy planning enters through `adapt`; legacy execution records must first become Magia-owned current evidence.

## Required inputs and evidence

Before writes, resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, required `spec_id`, evidence source, rigor profile, lifecycle stage, one internal mode, and the relevant payload. Prefer existing registry/package values, Nomia handoff, repository evidence, and prior validated planning over asking the user to repeat known facts. Record unresolved facts as assumptions or blockers; never invent repository, dependency, validation, or runtime truth. Load [evidence rules](references/evidence-contract.md) when claims depend on current state.

## Public workflow

Expose one lifecycle. For first use, unclear entrypoints, or a request for the next step, load [getting started](references/getting-started.md).


```text
clarify -> define -> analyze -> handoff -> reconcile
```

Select the least costly safe profile through [profiles and lifecycle](references/profiles-and-lifecycle.md):

- `quick`: one bounded, low-risk, well-understood change; four minimum package artifacts.
- `standard`: normal feature or technical change; quick set plus notes and triggered artifacts.
- `governed`: regulated, high-risk, contract/migration/security/operational, cross-service, or multi-repository work.

`quick` automatically escalates for ambiguity, contract or schema impact, migration/backfill, auth/security/privacy/compliance, material architecture, irreversible data change, unknown consumers, operational/rollback complexity, or multi-repository scope. A user request cannot force a forbidden shortcut.

Create files only through the [artifact decision matrix](references/artifact-decision-matrix.md). A template is not a creation trigger. Every artifact needs a trigger, owner, consumer, validator, retention rule, and non-duplication rationale.

For `standard` and `governed`, use [requirements and traceability](references/requirements-and-traceability.md), [clarification readiness](references/clarification-readiness.md), and [clarification prioritization](references/clarification-prioritization.md): EARS-style conditions/responses where useful, BCP 14 keywords only with normative meaning, Gherkin for observable acceptance, stable `REQ`, `AC`, `DECISION`, `task`, and `VAL` identifiers, and the governed chain `REQ -> AC -> DECISION -> TASK -> VALIDATION`.

## Internal mode router

Select exactly one write mode per mutation step; the public lifecycle may traverse several modes sequentially.

| Intent | Mode reference |
|---|---|
| discover repository candidates | [discovery](references/modes/discovery.md) |
| register/deduplicate/order specs and render external views | [order](references/modes/order.md) |
| normalize legacy/drifted planning | [adapt](references/modes/adapt.md) |
| seed a registry-backed package | [prepare-define](references/modes/prepare-define.md) |
| create or update a full package | [define](references/modes/define.md) / [refine](references/modes/refine.md) |
| product-only change | [define-product](references/modes/define-product.md) / [refine-product](references/modes/refine-product.md) |
| task-only change | [define-tasks](references/modes/define-tasks.md) / [refine-tasks](references/modes/refine-tasks.md) |
| architecture, contracts, migration, observability, security, rollback | [technical-design](references/modes/technical-design.md) |
| simplification/refactoring without behavior loss | [complexity-reduction](references/modes/complexity-reduction.md) |
| planned ADR | [architecture decisions](references/architecture-decisions.md) |
| reshape task plan | [reshape-tasks](references/modes/reshape-tasks.md) |
| compare Mago intent with Magia evidence | [reconcile](references/modes/reconcile.md) |

## Planning sequence

1. Route governance to Nomia and execution to Magia; retain only Mago-owned planning.
2. Resolve canonical identity and registry state before writes.
3. Select profile, lifecycle stage, and one internal mode.
4. Load [common planning](references/common-planning.md), then only branch-specific references.
5. Select artifacts through the decision matrix; use [technical standards](references/technical-artifact-standards.md), [ADR quality](references/adr-quality.md), and the [security-risk contract](references/security-risk-contract.md) only when triggered.
6. For existing-spec evolution, generate the external [change delta](references/change-delta.md) with added behavior, modified behavior, removed behavior, preserved behavior, compatibility impact, migration impact, and rollback assumptions; merge accepted intent into canonical artifacts and regenerate the delta.
7. For Spec Kit, Kiro, OpenSpec, C4, OpenAPI, AsyncAPI, or convergence work, use [interoperability and reconciliation](references/interoperability-and-reconciliation.md) and the [adapter development contract](references/adapter-development-contract.md). Validate imports; keep exports non-authoritative; disclose every known round-trip loss.
8. For multi-artifact writes, use the [mutation transaction and resume contract](references/mutation-transaction-and-resume.md) and `scripts/mutation_transaction.py`: fingerprint inspected state, stage outside canonical destinations, validate before atomic promotion, detect drift, resume safely, and require verified rollback after partial failure. Keep `manifest.yaml.mutation_state` non-clean until recovery completes.
9. When visibility helps, run `scripts/render_planning_compass.py` for the external [planning compass](references/planning-compass.md) or `scripts/render_execution_waves.py` for the [execution-wave projection](references/execution-wave-projection.md); both remain disposable and non-authoritative.
10. Handoff only validated intended work with a clean mutation state. Reconcile read-only and report: conforms to plan, execution deviation, unmet acceptance criteria, obsolete planned task, newly discovered work, required planning revision, or no-change convergence.

## Templates, scripts, and validation

Templates under `assets/templates/` are structural inputs, not defaults to copy blindly. Use `scripts/create_planning_identity.py` for identity/registry creation and `scripts/write_artifact_scaffold.py` for supported scaffolds. `scripts/mago_utils.py` and `scripts/concurrent_model.py` are import-only helpers, not CLIs. Load branch guidance only when triggered: [activation routing](references/activation-routing.md), [brownfield discovery summary](references/brownfield-discovery-summary.md), [operating rules](references/operating-rules.md), [roadmap evidence](references/roadmap-evidence-input.md), [RFC quality](references/rfc-quality.md), [planning-to-execution handoff](references/planning-execution-handoff.md), [validation and packaging](references/validation-and-packaging.md), or [installation and release](references/installation-and-release.md).

Use the relevant validators:

- artifact/package/repository: `scripts/validate_artifact.py`, `scripts/validate_package.py`, `scripts/validate_repo_board.py`; governed quality and triggered technical content: `scripts/validate_plan_quality.py`, `scripts/validate_clarification_readiness.py`, `scripts/validate_triggered_artifact.py`, `scripts/validate_security_risk.py --require-v2`;
- boundary/evidence/handoff/generated views: `scripts/validate_boundary.py`, `scripts/validate_evidence_contract.py`, `scripts/validate_planning_execution_handoff.py`, `scripts/validate_generated_view_contract.py`, `scripts/validate_planning_experience.py`;
- SDD semantics: `scripts/render_traceability.py`, `scripts/validate_traceability.py`, `scripts/validate_artifact_matrix.py`, `scripts/validate_change_delta.py`, `scripts/sdd_adapter.py`, `scripts/validate_sdd_adapter_report.py`, `scripts/reconcile_planning.py`;
- skill/package integrity: `scripts/validate_release_metadata.py`, `scripts/run_sdd_evidence_harness.py`, `scripts/merge_evidence_reports.py`, `scripts/validate_skill_package.py`, and `scripts/validate_distribution.py`; package only after all gates pass.

Required gates: canonical identity matches registry/package paths; feature keys are unique; dependencies resolve and are acyclic; generated views are reproducible; selected-profile artifacts and triggered technical concerns are complete; planning claims are evidenced or unresolved; changed behavior links to tasks and validation; new governed packages pass traceability and plan-quality v2 gates; new security plans use the v2 relational contract; adapter versions and losses are explicit; multi-artifact recovery is executable; reconciliation preserves Magia provenance and never claims Mago-authored runtime proof.

## Output contract

Return a concise Markdown report with these headings in order: `Planning context`, `Artifact decisions`, `Traceability`, `Risk and compatibility`, `Validation`, `Handoff or reconciliation`, and `Blockers`. Include profile and lifecycle stage; selected mode; resolved board/spec identity; evidence and assumptions; exact artifact paths created, updated, or skipped with matrix rationale; requirement/traceability status; compatibility, migration, security, operations, and rollback impacts when triggered; validator commands and exact outcomes; downstream result; and remaining work. Distinguish executed evidence from planned validation.

## Stop conditions

Stop before writes or readiness claims when identity/root is unresolved; registry/package state conflicts; evidence is insufficient for safe canonical intent; requested work belongs to Nomia or Magia; quick escalation is required but rejected; a second source of truth would be created; a generated view would be hand-edited; Magia evidence would be rewritten; runtime proof would be fabricated; required traceability, dependency, security, migration, compatibility, mutation-state, or package gates fail; protected fixtures/evaluators/reports/secrets are targeted; or packaging validation does not pass.
