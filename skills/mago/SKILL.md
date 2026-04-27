---
name: mago
description: use when asked to plan, normalize, audit, define, or refine canonical mago repository planning artifacts for a target repository or planning workspace under a resolved board root with concrete board_id and cycle_version; supports discovery, ordering, adapt, prepare-define, define, refine, technical-design, product-only planning, task-only planning, and task reshaping. do not use for implementation, code changes, runtime testing, deployment, release notes, delivery governance, portfolio reporting, stakeholder status, or noncanonical docs; require evidence-backed board_root resolution, one primary mode, validators, and planning-only output.
---

# MAGO

## Scope Boundary

MAGO owns repository planning artifacts under the canonical board model. Use it only when the output belongs under the resolved board root for a concrete `board_id` and `cycle_version`; package-scoped work also requires a concrete `spec_id`.

Owned outputs include discovery state, discovery index, discovery candidate docs, spec catalog, define queue, manifest, PRD, task plan, notes, validation plan, and spec-scoped technical design artifacts. Keep product code, runtime execution evidence, delivery governance, release notes, and ad hoc documentation outside MAGO scope.

When a request crosses from planning into execution, stop at the planning boundary and hand off to the appropriate execution workflow. Record unknowns as planning assumptions or blockers; do not invent repository truth.


## Activation Policy

Activate MAGO only when the user is asking to create, normalize, audit, or refine repository planning artifacts that belong in the canonical board model. Strong positive triggers include discovery of repository candidates, ordering a backlog into the define queue, adapting legacy planning docs, preparing define-ready package shells, defining or refining a spec package, producing a spec-scoped technical design, reshaping tasks, or separating product-only and task-only planning.

Do not activate MAGO for implementation, product-code edits, runtime testing, deployment, operational evidence collection, delivery governance, release notes, stakeholder status, portfolio reporting, or general documentation outside the resolved board root. When a prompt mixes planning with execution or governance, keep only the planning portion in MAGO scope and hand off the rest instead of creating execution or governance artifacts.

For ambiguous prompts, first decide whether the requested output is a canonical MAGO artifact under BOARD_ROOT. If not, do not use MAGO. If the user likely wants MAGO but omits board_id, cycle_version, BOARD_ROOT, or spec_id needed by the selected mode, stop before writing and ask for the smallest missing input.

## Required Inputs

Resolve these inputs before writing or changing any MAGO artifact:

- `BOARD_ROOT`: active canonical board root resolved through [references/canonical-paths.md](references/canonical-paths.md) or supplied explicitly.
- `board_id` and `cycle_version`: required concrete path segments for board-scoped work.
- `spec_id`: required for package-scoped modes under `BOARD_ROOT/specs/<spec_id>/`.
- Target repository or planning workspace: the evidence source used to inspect existing planning artifacts.
- Mode intent and evidence payload: the user request, roadmap evidence, artifact content, or package state needed for the selected mode.

If the board root, board id, or cycle version cannot be derived safely, do not create parallel planning files. Ask the smallest missing-input question or stop with the blocker named explicitly.


## Evidence Discipline

Use repository contents, existing planning artifacts, roadmap evidence, user-provided context, and validated package state as truth sources. Treat absent evidence as an unresolved assumption or blocker. Do not infer hidden repository facts, owner commitments, dependency status, implementation completion, or validation results from naming conventions alone.

Before writing, identify the evidence payload for the selected mode. During writing, preserve source-to-artifact traceability in notes, validation, or package metadata when the applicable mode reference requires it. After writing, report which assumptions remain unresolved instead of silently filling gaps. Load [references/evidence-contract.md](references/evidence-contract.md) when planning claims depend on repository truth, execution state, validation state, dependency state, or source traceability.

## Mode Selection Matrix

Choose exactly one primary mode before loading mode details.

| User intent | Mode | Required inputs | Primary outputs | Final validator |
|---|---|---|---|---|
| discover repository features or candidate work | `discovery` | repo evidence, board id, cycle version | discovery state, discovery index, discovery candidate docs | `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` if board artifacts changed |
| order discovered candidates into the board backlog | `order` | discovery artifacts, ordering evidence | spec catalog and define queue | `scripts/validate_artifact.py`, then `scripts/validate_repo_board.py` |
| adapt drifted or legacy planning docs into canonical board shape | `adapt` | existing planning docs, canonical board path | normalized board or package artifacts | `scripts/validate_artifact.py`, package or repo validators as applicable |
| seed define-ready package shells from ordered work | `prepare-define` | define queue, selected spec ids | package scaffolds under `BOARD_ROOT/specs/` | `scripts/validate_package.py` and `scripts/validate_repo_board.py` |
| define a full spec package | `define` | spec id, roadmap or repository evidence | manifest, PRD, tasks, notes, validation | `scripts/validate_package.py` |
| refine a full spec package without changing mode boundaries | `refine` | existing package, requested planning corrections | updated package artifacts | `scripts/normalize_package.py` when useful, then `scripts/validate_package.py` |
| align architecture or contracts for one selected spec | `technical-design` | spec id, architecture evidence | spec-scoped technical design | `scripts/validate_technical_design.py` or `scripts/validate_artifact.py` |
| reshape broad task plans into canonical task structure | `reshape-tasks` | task plan evidence, selected package | updated task plan and related status fields | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| define product-only artifacts | `define-product` | product evidence, spec id | product docs only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| refine product-only artifacts | `refine-product` | existing product docs, requested corrections | updated product docs only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| define task-only artifacts | `define-tasks` | product baseline, task evidence, specialist needs | task plan only | `scripts/validate_artifact.py` and `scripts/validate_package.py` |
| refine task-only artifacts | `refine-tasks` | existing task plan, requested corrections | updated task plan only | `scripts/normalize_package.py` when useful, then `scripts/validate_package.py` |

## Progressive Loading Workflow

1. Select one mode from the matrix and refuse mode mixing.
2. Open [references/canonical-paths.md](references/canonical-paths.md) and resolve `BOARD_ROOT` before any write.
3. Open [references/common-planning.md](references/common-planning.md) for shared planning rules.
4. Open exactly one primary mode reference from [references/modes/](references/modes/): `discovery`, `order`, `adapt`, `prepare-define`, `define`, `refine`, `technical-design`, `reshape-tasks`, `define-product`, `refine-product`, `define-tasks`, or `refine-tasks`.
5. Open additional references only when their condition applies:
   - [references/artifacts/discovery-order.md](references/artifacts/discovery-order.md) for discovery, ordering, or define-handoff structure.
   - [references/artifacts/templates-and-status.md](references/artifacts/templates-and-status.md) for package structure, status fields, or template-backed artifact consistency.
   - [references/artifacts/technical-design.md](references/artifacts/technical-design.md) for spec-scoped architecture artifacts.
   - [references/markdown-writing.md](references/markdown-writing.md) for Markdown quality.
   - [references/rfc-quality.md](references/rfc-quality.md) for PRD assumptions, options, and unresolved decisions.
   - [references/adr-quality.md](references/adr-quality.md) for notes, design decisions, and trade-offs.
   - [references/specialist-spellbook.md](references/specialist-spellbook.md) for task specialist metadata.
   - [references/roadmap-evidence-input.md](references/roadmap-evidence-input.md) for roadmap-sourced define or refine work.
   - [references/operating-rules.md](references/operating-rules.md) when scope, handoff, or artifact ownership is ambiguous.
   - [references/activation-routing.md](references/activation-routing.md) when activation, negative triggers, ambiguous routing, regression, or adversarial routing need scenario-backed review.
   - [references/evidence-contract.md](references/evidence-contract.md) when repository facts, traceability, execution-state, validation-state, or dependency claims need explicit evidence controls.
   - [references/validation-and-packaging.md](references/validation-and-packaging.md) before final package validation or when validating the skill package itself.
6. Use [assets/templates/](assets/templates/) through scripts rather than freehand copying whenever creating supported artifacts.
7. Use [assets/flows/discovery-order-prepare-define-loop.md](assets/flows/discovery-order-prepare-define-loop.md) only for multi-step planning flows that explicitly stay within discovery, ordering, and define-preparation boundaries.
8. Use [scripts/](scripts/) for scaffolding, list updates, normalization, artifact validation, board validation, boundary checks, and package-level skill validation.
9. Review [examples/activation-scenarios.json](examples/activation-scenarios.json) when activation or refusal behavior needs scenario evidence.

## Template Asset Contract

Use template-backed artifact creation instead of freehand structure whenever a supported artifact is created or normalized. Prefer `scripts/write_artifact_scaffold.py` for new files and `scripts/update_template_lists.py` for supported list fields. The operational templates are:

- `assets/templates/discovery-state.json.template` for discovery run state.
- `assets/templates/discovery-index.yaml.template` for discovery indexes.
- `assets/templates/discovery-candidate.md.template` for discovery candidate records.
- `assets/templates/spec-catalog.yaml.template` for ordered spec catalog entries.
- `assets/templates/define-queue.yaml.template` for define queue handoff records.
- `assets/templates/manifest.yaml.template` for package manifests and source-of-truth metadata.
- `assets/templates/prd.md.template` for product requirement documents.
- `assets/templates/tasks.md.template` for canonical task plans.
- `assets/templates/notes.md.template` for package notes, decisions, and assumptions.
- `assets/templates/validation.md.template` for validation plans and recorded validator outcomes.
- `assets/templates/technical-design.md.template` for spec-scoped architecture alignment.

Do not copy template placeholders into final artifacts unless the selected mode explicitly creates a scaffold. For completed planning artifacts, replace dynamic fields with evidence-backed values or record the unresolved value as an assumption, blocker, or open question.

## Scenario and Package Quality Contract

Activation behavior is part of MAGO package quality. Keep `examples/activation-scenarios.json` as the deterministic oracle used by `scripts/validate_activation_scenarios.py` and keep `evals/activation-scenarios.json` as the planned prompt-review suite for future live or human evaluation. Update both when activation boundaries, mode routing, stop conditions, or handoff rules materially change.

Before packaging the MAGO skill itself, run the package-level gates in [references/validation-and-packaging.md](references/validation-and-packaging.md). Treat deterministic scenario metrics as static oracle evidence only; do not claim live activation precision or recall unless the prompts were executed and the results were recorded.

## Script Routing

- Create new template-backed artifacts with `scripts/write_artifact_scaffold.py`.
- Populate supported list fields with `scripts/update_template_lists.py`; check supported schemas with its `--schema` option before editing by hand.
- Validate any touched MAGO artifact with `scripts/validate_artifact.py` so validator selection is mechanical.
- Validate package-scoped work with `scripts/validate_package.py`.
- Validate board-scoped work with `scripts/validate_repo_board.py`.
- Validate spec-scoped architecture artifacts with `scripts/validate_technical_design.py`.
- Normalize legacy package drift with `scripts/normalize_package.py` when the change is mechanical and evidence-preserving.
- Validate activation, ambiguity, refusal, and mode-routing scenarios with `scripts/validate_activation_scenarios.py` during hardening or packaging.
- Validate MAGO skill package integrity with `scripts/validate_skill_package.py` during hardening or packaging.
- Build and archive the MAGO skill itself with `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate` only after package-level gates pass.
- Validate package evidence and traceability with `scripts/validate_evidence_contract.py` when touched artifacts include repository facts, execution-state, validation-state, dependency-state, or source-of-truth claims.
- Run `scripts/validate_boundary.py` when changes could blur MAGO planning boundaries with governance or execution workflows.


## Validation Gates

A MAGO run is incomplete until every touched artifact family has an explicit validator outcome. Use script output as measured evidence only when the command was actually run. If a validator fails and the failure cannot be corrected within MAGO planning scope, stop and report the blocker.

Required gates are: exactly one primary mode selected; BOARD_ROOT, board_id, and cycle_version resolved before writes; spec_id resolved for package-scoped work; all writes stay under BOARD_ROOT or the selected package; template-backed artifacts are created or normalized through scripts when supported; referenced planning facts are evidence-backed or recorded as unresolved; evidence and traceability are validated when package claims depend on repository truth; activation and boundary behavior remains covered by examples/activation-scenarios.json during hardening or packaging.

## Output Contract

For every in-scope MAGO run, the final response must include:

- selected mode and why it was the only primary mode used;
- resolved `BOARD_ROOT`, `board_id`, `cycle_version`, and `spec_id` when package-scoped;
- touched artifacts grouped by canonical board or package path;
- scaffold, normalization, update, and validator commands run, with pass or fail outcome;
- unresolved inputs, assumptions, or blocked changes recorded in planning artifacts instead of invented;
- handoff note when the user requested implementation, execution evidence, or governance outside MAGO scope.

Do not include product-code diffs, runtime execution proof, or non-canonical planning files as MAGO output.

## Stop Conditions

Stop before editing when any condition applies:

- the active mode cannot be selected without mixing primary modes;
- `BOARD_ROOT`, `board_id`, or `cycle_version` is missing and cannot be derived;
- a requested artifact path is outside the resolved board root or would create a duplicate board tree;
- the user asks for implementation code, task execution, runtime evidence, or delivery governance after planning;
- a required template script or validator is unavailable and the change would require freehanding template structure;
- validation fails and cannot be fixed within MAGO planning scope.

When stopping, name the blocked mode decision, the missing or unsafe input, and the canonical path required to continue.

## Finalization Checklist

Before claiming completion:

- all writes are under `BOARD_ROOT` or the selected package path;
- every dynamic id, status, dependency, and ordering decision is evidence-backed or recorded as unresolved;
- template-backed artifacts were created or updated through scripts when supported;
- validators for the touched artifact family passed, or failures are reported as blockers;
- final response reports commands, touched files, assumptions, and handoff boundaries.
