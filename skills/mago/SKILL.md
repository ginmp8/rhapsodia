---
name: mago
description: use when asked to plan, normalize, audit, define, or refine tech-lead owned repository planning artifacts for a resolved board and cycle, including concurrent-safe spec registration, prd refinement, technical design, complexity reduction, architecture decisions, tasks, validation, migrations, observability, security, discovery, ordering, and define or refine workflows. do not use for implementation, delivery governance, status reporting, runtime testing, deployments, commits, pull requests, or magia execution records.
---

# MAGO

Tech-lead planning skill. Convert governance intake plus repository evidence into one canonical planning model. MAGO owns intended design and planning contracts; it does not implement code, collect runtime proof, deploy, commit, open pull requests, or maintain delivery governance.

## Canonical Model

```text
docs/boards/<board_id>/<year>/cycles/<cycle_id>/
  cycle.yaml
  discovery-state.json
  discovery-index.yaml
  candidates/<candidate_id>.md
  registry/<spec_id>.yaml
  specs/<spec_id>/
```

`cycle_id` and `spec_id` are immutable, date-readable ULID identities. Each spec has an independent registry file so unrelated workers do not edit a shared catalog. Semantic feature or delivery versions are metadata only and never define filesystem identity. Catalog and queue views are generated outside the canonical tree and are never hand-edited source of truth.

Old planning layouts are not an alternative MAGO model. When they must be retained, treat them only as read-only migration input to `adapt`, then write the canonical model.

Load [references/canonical-paths.md](references/canonical-paths.md), [references/concurrent-planning.md](references/concurrent-planning.md), and [references/common-planning.md](references/common-planning.md) before writes.

## Scope and Ownership

MAGO writes only canonical planning artifacts: cycle metadata, discovery state/index/candidates, per-spec registry records, manifest, PRD, tasks, notes, validation, technical design, complexity-reduction plans, planned architecture decisions/ADRs, execution handoff plans, contract specs, migration strategies, observability designs, operational requirements, security/risk considerations, and open questions.

Routing boundaries:

- nomia owns intake, governance, delivery status, stakeholder communication, roadmap bookkeeping, release notes, and accepted business risk;
- MAGO owns intended technical planning and planned decisions;
- MAGIA owns implementation, runtime validation, execution records, task completion evidence, commits, pull requests, and deployments.

MAGO may consume repository truth, governance intake, and MAGIA evidence as read-only input. It must preserve truthful history and never fabricate repository, execution, validation, approval, or completion facts. A MAGO planning boundary is an authoring boundary, not an implementation prohibition: execution-required tasks are valid planning outputs when they are bounded, evidence-backed, explicitly handed to MAGIA, and paired with a credible validation path.

## Activation Policy

Activate for creating, normalizing, auditing, or refining canonical repository planning artifacts. Strong triggers include discovery, concurrent-safe registration, ordering, prepare-define, define/refine, PRD refinement, technical design, architecture decisions, complexity reduction, task reshaping, validation planning, and migration of old planning input into the canonical model.

Do not activate for code implementation, runtime tests, deployment, operational evidence, governance/status work, release notes, stakeholder communication, or general documentation outside a planning board.

Before writes, resolve:

- `BOARD_ROOT` or enough identifiers to derive it;
- `board_id`, `year`, and `cycle_id`;
- `spec_id` for package-scoped work;
- evidence source and payload;
- exactly one primary mode.

If required identity or repository truth is missing, stop before writing and request only the smallest missing input.

## Modes

Select exactly one primary mode.

| Mode | Owns | Key validation |
|---|---|---|
| `discovery` | discovery state/index/candidate docs | artifact validator, then board validator |
| `order` | one or more independent registry entries | board validator |
| `adapt` | old-layout intake or canonical drift normalization | artifact/package/board validators |
| `prepare-define` | seed one registered package | package and board validators |
| `define` | one full package | package validator |
| `refine` | bounded update to one package | normalization when useful, then package validator |
| `technical-design` | one spec technical design | technical-design validator |
| `complexity-reduction` | evidence-backed simplification/refactoring plan | artifact and package validators |
| `architecture-decision` | planned architecture decision/ADR | artifact validator or static ADR review |
| `reshape-tasks` | task-plan reshaping | artifact and package validators |
| `define-product` / `refine-product` | product planning files only | artifact and package validators |
| `define-tasks` / `refine-tasks` | task plan only | artifact validator; refine may normalize first |

Do not mix primary modes in one pass. A multi-stage request must execute bounded stages sequentially, each with its own validator outcome.

## Workflow

1. Select one primary mode.
2. Resolve `BOARD_ROOT` through [references/canonical-paths.md](references/canonical-paths.md).
3. Load [references/concurrent-planning.md](references/concurrent-planning.md) for identity, registry, dependency, and generated-view rules.
4. Load [references/common-planning.md](references/common-planning.md).
5. Load exactly one primary mode reference under `references/modes/`.
6. Load conditional references only when triggered: `references/artifacts/templates-and-status.md` for canonical artifact/task contracts; technical artifact standards; architecture decisions; complexity reduction; shared ownership; evidence contract; activation routing; planning/execution handoff; operating rules; and validation/packaging.
7. Use scripts for identity creation, scaffolding, rendering, normalization, and validation. Do not manually invent IDs or shared aggregate files.
8. Run the validator for every touched artifact family.

## Script and Template Contract

Use:

- `scripts/create_planning_identity.py` to atomically create cycle and spec identities;
- `scripts/write_artifact_scaffold.py` for template-backed artifacts;
- `scripts/render_registry_views.py` for deterministic, noncanonical catalog/queue views;
- `scripts/validate_concurrent_board.py` for identity, registry, dependency, duplicate-feature, package, and DAG checks;
- `scripts/validate_repo_board.py` as the board validation entrypoint;
- `scripts/validate_package.py`, `scripts/validate_technical_design.py`, and `scripts/validate_evidence_contract.py` for package-level checks;
- `scripts/normalize_package.py` for bounded package normalization and old execution-section detection;
- `scripts/validate_skill_package.py` and `scripts/package_skill.py` before distribution.

Templates are structural inputs. Create cycles from `assets/templates/cycle.yaml.template` and registry entries from `assets/templates/spec-registry-entry.yaml.template`. Replace dynamic tokens with evidence-backed values or explicit assumptions/blockers. Never create or hand-edit generated catalog and define-queue views as source of truth.

## Validation Gates

A run is incomplete until all touched families have validator outcomes. Required gates:

- exactly one mode;
- resolved canonical root;
- IDs generated or validated, not manually sequenced;
- writes contained under the resolved root/package;
- no duplicate active `feature_key` within a cycle;
- all spec dependencies resolve and the dependency graph is acyclic;
- registry and package manifests agree on immutable identities;
- generated views reproduce deterministically when requested;
- planning claims are evidence-backed or explicitly unresolved;
- no MAGIA execution evidence is fabricated or rewritten;
- `scripts/validate_planning_execution_handoff.py` passes when package or handoff contracts change;
- `scripts/validate_generated_view_contract.py` passes when renderer or generated-view templates change.

When validation fails outside MAGO planning authority, stop and report the blocker.

## Output Contract

Final responses state:

- selected mode and why it was the only mode;
- resolved `BOARD_ROOT`;
- `board_id`, `year`, `cycle_id`, and `spec_id` when applicable;
- touched artifacts grouped by canonical path;
- identity/scaffold/render/normalization/validation commands and outcomes;
- decisions, assumptions, trade-offs, risks, duplicate/dependency findings, and unresolved questions;
- downstream handoff for execution or governance work outside MAGO scope.

Do not claim runtime proof, implementation completion, governance approval, or package readiness without corresponding evidence.

## Stop Conditions

Stop before editing when:

- primary modes would be mixed;
- the canonical root or required IDs cannot be resolved;
- a requested write targets an old layout instead of adapting it into the canonical tree;
- a requested path duplicates or bypasses the registry model;
- the user requests implementation, runtime evidence, governance/status work, or release communication;
- a technical decision requires current runtime evidence only MAGIA can produce;
- template or validator support is unavailable and freehand structure would be required;
- validation reports an unresolvable identity collision, dependency cycle, duplicate active feature, or boundary violation.

## Finalization Checklist

Before completion, verify: all writes are contained; IDs are immutable and valid; registry files are the source of truth; no shared aggregate was hand-edited; package identity matches registry identity; dependencies are valid and acyclic; templates/scripts were used; validators passed or blockers were reported; no generated noise, caches, secrets, or old packages were added; and final reporting separates observed, inferred, planned, and measured evidence.
