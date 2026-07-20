---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board/spec package, including prd refinement from governance intake, technical design, complexity-reduction strategy, refactoring plans, architecture decisions, planned-decision records, execution handoff plans, tasks, validation plans, contract specs, migrations, observability, operations, security/risk notes, discovery, ordering, and define/refine workflows. do not use for execution work, delivery governance/status reporting, stakeholder communication, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Plan intended technical work from Nomia intake and repository evidence. Mago owns planning; it does not implement code, deploy, commit, open PRs, accept business risk, or own delivery governance. Mago does not fabricate runtime evidence.

## Authority and canonical state

- Nomia owns requester, owner, due date, priority, stakeholders, roadmap, status, release notes, and governance decisions.
- Mago owns intended requirements, design, decisions, tasks, validation plans, technical risks, and execution handoff.
- Magia owns implementation and runtime evidence. Mago may read Magia evidence only for reconciliation and must not rewrite it.
- A Mago planning boundary is an authoring boundary, not an execution prohibition: execution-required tasks are valid planning outputs when bounded, evidenced, assigned to downstream Magia, and paired with a validation path. Mago never performs those tasks.

Write only under a resolved `BOARD_ROOT` using [canonical paths](references/canonical-paths.md) and [concurrent identity/registry rules](references/concurrent-planning.md). Immutable cycle/spec identity and registry state are authoritative; generated catalogs, queues, deltas, adapters, traceability matrices, and reconciliation reports are non-authoritative deterministic projections. Never create parallel trees, mutable sequence counters, duplicate `feature_key` records, or manually edited generated views.

Use [shared ownership](references/shared-artifact-ownership.md) whenever Mago and Magia touch the same package. Legacy planning enters through `adapt`; legacy execution records must first become Magia-owned current evidence.

## Inputs and evidence

Before writes, resolve `BOARD_ROOT`, `board_id`, `year`, `cycle_id`, required `spec_id`, evidence source, rigor profile, lifecycle stage, one internal mode, and the relevant payload. Prefer existing registry/package values, Nomia handoff, repository evidence, and prior validated planning over asking the user to repeat known facts. Record unresolved facts as assumptions or blockers; never invent repository, dependency, validation, or runtime truth. Load [evidence rules](references/evidence-contract.md) when claims depend on current state.

## Public workflow

Expose one lifecycle:

```text
clarify -> define -> analyze -> handoff -> reconcile
```

Select the least costly safe profile through [profiles and lifecycle](references/profiles-and-lifecycle.md):

- `quick`: one bounded, low-risk, well-understood change; four minimum package artifacts.
- `standard`: normal feature or technical change; quick set plus notes and triggered artifacts.
- `governed`: regulated, high-risk, contract/migration/security/operational, cross-service, or multi-repository work.

`quick` automatically escalates for ambiguity, contract or schema impact, migration/backfill, auth/security/privacy/compliance, material architecture, irreversible data change, unknown consumers, operational/rollback complexity, or multi-repository scope. A user request cannot force a forbidden shortcut.

Create files only through the [artifact decision matrix](references/artifact-decision-matrix.md). A template is not a creation trigger. Every artifact needs a trigger, owner, consumer, validator, retention rule, and non-duplication rationale.

For `standard` and `governed`, use [requirements and traceability](references/requirements-and-traceability.md): EARS-style conditions/responses where useful, BCP 14 keywords only with normative meaning, Gherkin for observable acceptance, stable `REQ`, `AC`, `DECISION`, `task`, and `VAL` identifiers, and the governed chain `REQ -> AC -> DECISION -> TASK -> VALIDATION`.

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
5. Select artifacts through the decision matrix; use [technical standards](references/technical-artifact-standards.md) and [ADR quality](references/adr-quality.md) only when triggered.
6. For existing-spec evolution, generate the external [change delta](references/change-delta.md) with added behavior, modified behavior, removed behavior, preserved behavior, compatibility impact, migration impact, and rollback assumptions; merge accepted intent into canonical artifacts and regenerate the delta.
7. For Spec Kit, Kiro, OpenSpec, C4, OpenAPI, AsyncAPI, or convergence work, use [interoperability and reconciliation](references/interoperability-and-reconciliation.md). Validate imports; keep exports non-authoritative; disclose every known round-trip loss.
8. Create/refresh supported artifacts from templates through scripts, replace placeholders with evidence, then run the narrowest artifact validator and broader package/repository gates.
9. Handoff only validated intended work. Reconcile read-only and report: implemented as planned, implementation deviation, unmet acceptance criteria, obsolete planned task, newly discovered work, required planning revision, or no-change convergence.

## Templates, scripts, and validation

Templates under `assets/templates/` are structural inputs, not defaults to copy blindly. Use `scripts/create_planning_identity.py` for identity/registry creation and `scripts/write_artifact_scaffold.py` for supported scaffolds. `scripts/mago_utils.py` and `scripts/concurrent_model.py` are import-only helpers, not CLIs.

Use the relevant validators:

- artifact/package/repository: `scripts/validate_artifact.py`, `scripts/validate_package.py`, `scripts/validate_repo_board.py`;
- boundary/evidence/handoff/generated views: `scripts/validate_boundary.py`, `scripts/validate_evidence_contract.py`, `scripts/validate_planning_execution_handoff.py`, `scripts/validate_generated_view_contract.py`;
- SDD semantics: `scripts/render_traceability.py`, `scripts/validate_traceability.py`, `scripts/validate_artifact_matrix.py`, `scripts/validate_change_delta.py`, `scripts/validate_sdd_adapter_report.py`, `scripts/reconcile_planning.py`;
- skill/package integrity: `scripts/validate_skill_package.py`, then `scripts/package_skill.py` only after all gates pass.

Required gates: canonical identity matches registry/package paths; feature keys are unique; dependencies resolve and are acyclic; generated views are reproducible; selected-profile artifacts and triggered technical concerns are complete; planning claims are evidenced or unresolved; changed behavior links to tasks and validation; governed golden/package traceability is complete; adapters disclose losses; reconciliation preserves Magia provenance and never claims Mago-authored runtime proof.

## Output contract

Report: profile and lifecycle stage; selected mode; resolved board/spec identity; evidence and assumptions; artifacts created/updated/skipped with matrix rationale; requirement/traceability status; compatibility, migration, security, operations, and rollback impacts when triggered; validators and exact outcomes; handoff or reconciliation result; blockers and remaining work. Distinguish executed evidence from planned validation.

## Stop conditions

Stop before writes or readiness claims when identity/root is unresolved; registry/package state conflicts; evidence is insufficient for safe canonical intent; requested work belongs to Nomia or Magia; quick escalation is required but rejected; a second source of truth would be created; a generated view would be hand-edited; Magia evidence would be rewritten; runtime proof would be fabricated; required traceability, dependency, security, migration, compatibility, or package gates fail; protected fixtures/evaluators/reports/secrets are targeted; or packaging validation does not pass.
