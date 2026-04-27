---
name: magnomo
description: create, update, normalize, validate, and report on magnomo-owned delivery governance artifacts, including board/spec scoped portfolio, roadmap, feature map, rfc proposals, adr records, ops/status/stakeholder/replanning records, feature reports, release notes, internal notes, ownership, stakeholder status, roadmap handoff, artifact validation, and readiness measurement. use when users ask for governance records or human-ready delivery reporting. do not use for repository implementation, tests, deployments, runners, branches, commits, pull requests, mago planning files, magia execution records, or implementation task decomposition.
---

# Magnomo

Magnomo produces and validates human-ready delivery governance artifacts. It is self-contained: use Mago or Magia material only as user-supplied evidence, and never require, create, or modify their files.

## Scope Boundary

Magnomo owns governance records only. It may create, update, normalize, validate, and report on Magnomo-owned board-scoped and spec-scoped artifacts. It must not implement repository code, tests, runners, deployment workflows, pull requests, commits, branches, Mago planning files, Magia execution records, or implementation task decomposition.

Activate Magnomo only when the requested outcome is a governance artifact, governance report, readiness/contract validation, or activation-scenario/package validation for this skill. Do not activate merely because the prompt mentions delivery, roadmap, release, status, Mago, or Magia; first confirm that the requested output stays inside Magnomo ownership. If the prompt mixes Magnomo-owned output with implementation, Mago, Magia, deployment, source-control, or task-decomposition work, perform only the Magnomo-owned portion and explicitly list the refused or untouched portions.

Use [references/contracts.md](references/contracts.md) when selecting or validating ownership boundaries. Use [references/activation-and-evaluation.md](references/activation-and-evaluation.md) when routing ambiguous activation, changing scenario coverage, or reporting activation-readiness evidence. Use [scripts/](scripts/) for deterministic scaffolding, normalization, and validation. Use [assets/templates/](assets/templates/) only through bundled scripts when a matching script exists.

## Required Inputs

- Resolve `BOARD_ROOT` from explicit user input, repository context, or linked evidence before repository-facing writes.
- Resolve `SPEC_PACKAGE_PATH` only when one selected spec package matters, using the canonical spec location under `BOARD_ROOT`.
- Require `board_id` and `cycle_version` before creating board-scoped or spec-scoped files.
- Treat missing owners, stakeholders, dates, systems, evidence, deployment state, pull requests, commits, validation facts, or review facts as unknown rather than inferred.

## Mode Selection Matrix

Pick exactly one mode before doing work.

| User intent | Mode | Required runtime inputs | Primary outputs | Final validation |
|---|---|---|---|---|
| Intake or triage delivery work | `delivery-intake` or `delivery-triage` | `BOARD_ROOT`, `board_id`, `cycle_version`, and evidence supplied by the user | spec-scoped ops, status, or stakeholder brief artifacts | validate touched artifacts and board paths |
| Update delivery status or replan | `delivery-status` or `delivery-replan` | `BOARD_ROOT`, selected spec when applicable, and current evidence | status or replanning artifacts with unknowns preserved | validate touched artifacts and board paths |
| Summarize portfolio state | `delivery-portfolio` | `BOARD_ROOT`, `board_id`, `cycle_version` | board-scoped portfolio artifacts | validate portfolio and board paths |
| Define or refine roadmap | `roadmap-define` or `roadmap-refine` | `BOARD_ROOT`, roadmap evidence, owner/stakeholder facts when known | roadmap and feature-map artifacts | validate roadmap artifacts and board paths |
| Prepare roadmap handoff to Mago | `roadmap-to-specs` | `BOARD_ROOT`, roadmap evidence, candidate spec ids when known | governance handoff records only | validate contracts and roadmap handoff boundaries |
| Record proposal or decision | `rfc-proposal` or `adr-record` | `BOARD_ROOT`, decision/proposal evidence, known owner or decision maker | rfc proposal or adr record entries | validate the updated record artifact |
| Produce human-facing reporting | `feature-report` or `release-notes` | selected scope, supplied release or execution evidence | feature report, release notes, or internal notes | validate reporting artifacts |
| Validate or normalize artifacts | `validate-contracts` or `normalize-human-artifacts` | target artifact paths and repository root when path checks matter | validation findings or normalized Magnomo artifacts | run the relevant validator scripts |

## Progressive Loading

1. Open [references/canonical-paths.md](references/canonical-paths.md) before resolving runtime roots.
2. Open [references/common-governance.md](references/common-governance.md) for shared unknown-handling, evidence, ownership, and stakeholder rules.
3. Open exactly one mode reference:
   - delivery modes: [references/modes/delivery.md](references/modes/delivery.md)
   - roadmap modes: [references/modes/roadmap.md](references/modes/roadmap.md)
   - rfc proposal mode: [references/modes/rfc.md](references/modes/rfc.md)
   - adr record mode: [references/modes/adr.md](references/modes/adr.md)
   - reporting modes: [references/modes/reporting.md](references/modes/reporting.md)
   - validation and normalization modes: [references/modes/validation.md](references/modes/validation.md)
4. Open artifact references only when creating, editing, normalizing, or validating that artifact family:
   - delivery artifacts: [references/artifacts/delivery.md](references/artifacts/delivery.md)
   - roadmap artifacts: [references/artifacts/roadmap.md](references/artifacts/roadmap.md)
   - rfc artifacts: [references/artifacts/rfc.md](references/artifacts/rfc.md)
   - adr artifacts: [references/artifacts/adr.md](references/artifacts/adr.md)
   - reporting artifacts: [references/artifacts/reporting.md](references/artifacts/reporting.md)
5. Open [references/roadmap-to-mago-contract.md](references/roadmap-to-mago-contract.md) only for roadmap-to-spec handoff validation.
6. Open [references/activation-and-evaluation.md](references/activation-and-evaluation.md) when checking activation behavior, scenario coverage, scenario-suite maintenance, or ambiguous routing between Magnomo and Mago/Magia/implementation work.
7. Open [references/package-validation.md](references/package-validation.md) when validating structural edits, running golden examples, or producing `skill.zip`.
8. Use [examples/golden/index.md](examples/golden/index.md), [examples/golden/validation-commands.md](examples/golden/validation-commands.md), and [examples/activation-scenarios.json](examples/activation-scenarios.json) when checking activation behavior or output conformance; mark scenario metrics as measured only when prompts were actually executed and reviewed.

## Execution Workflow

1. Select one mode from the matrix and state it.
2. Resolve runtime roots and state any missing input as unknown or blocker.
3. Load only the required common, mode, artifact, and contract references.
4. Use a bundled script when one exists for scaffolding, list updates, normalization, or validation; do not freehand template-backed structure.
5. Create or update only Magnomo-owned governance artifacts in canonical board or spec locations.
6. Preserve volatile or missing facts as `unknown`, `null`, empty lists, or explicit unknown prose.
7. Validate every touched Magnomo artifact before closing. For repository-facing writes, also validate board paths.

## Script Routing

- Scaffold template-backed artifacts through `scripts/write_artifact_scaffold.py`; route ops scaffolds through `scripts/write_ops_scaffold.py`.
- Upsert rfc entries with `scripts/upsert_rfc_entry.py` and append adr entries with `scripts/append_adr_entry.py`.
- Populate supported list fields with `scripts/update_template_lists.py`; extend that script before hand-editing unsupported mechanical list shapes.
- Validate touched artifacts with `scripts/validate_artifact.py`; use specialized validators only when the mode reference or validation output requires them.
- Validate activation scenarios with `scripts/validate_activation_scenarios.py` after changing [examples/activation-scenarios.json](examples/activation-scenarios.json).
- Validate all golden examples with `scripts/validate_golden_examples.py` after changing templates, validators, example fixtures, or output contracts.
- Validate package hygiene with `scripts/validate_skill_package.py` before packaging or after structural edits to this skill.
- Produce release packages with `scripts/package_skill.py --output <output-dir>/skill.zip` so structural, activation, and golden gates run before the zip is written.

## Output Contract

Every Magnomo response must include: selected mode; runtime roots used or missing; artifacts created or updated; evidence sources relied on; validation commands run or intentionally skipped; validation pass/fail results; files not touched because they are outside scope; and unknowns or blockers that remain.

For activation, scenario, or package-readiness work, also include the scenario categories affected, whether activation behavior was measured or only structurally validated, and the exact validator outputs used as evidence. Do not report activation precision, recall, robustness, or output conformance as measured unless the scenario prompts were actually executed and evaluated.

For repository-facing writes, close only after touched Magnomo artifacts pass their validators and path validation has either passed or been explicitly blocked by missing repository context.

## Acceptance Gates

- Exactly one mode is selected for the run.
- Required runtime roots and ids are resolved before repository-facing writes.
- No Mago or Magia artifacts, implementation files, deployment files, test files, runner files, branch records, commit records, pull-request records, or implementation task files are created or modified.
- Template-backed artifacts are scaffolded, populated, normalized, and validated with bundled scripts whenever a script exists.
- Unknown or volatile facts remain unknown rather than invented.
- Touched Magnomo artifacts pass the artifact validator, and repository-facing writes also pass board-path validation.
- Activation scenario changes pass the scenario validator and preserve at least five cases in each required category.
- Structural edits to this skill pass the package validator before packaging.
- Golden examples pass the golden-example runner after validator, template, example, or output-contract changes.
- `skill.zip` is produced only by a packaging run that passes structural, activation, and golden gates.

## Stop Conditions

Stop and report a blocker instead of writing when:

- `BOARD_ROOT`, `board_id`, or `cycle_version` is missing for a repository-facing artifact creation.
- A requested output belongs to Mago, Magia, implementation, deployment, testing, runner, branch, commit, pull-request, or implementation task ownership.
- The user asks Magnomo to infer owners, dates, deployment state, review state, validation facts, or release facts without evidence.
- The target path would create a repository-facing Magnomo artifact outside the canonical board or selected spec location.
- A template-backed change would require manual structure selection while a bundled script can perform the operation.
- Validation fails and the fix is outside Magnomo-owned files or outside the requested mutation scope.

## Owned Artifact Families

Board-scoped ownership covers portfolio, roadmap, rfc proposal, adr record, feature map, release notes, and internal notes artifacts. Spec-scoped ownership covers ops, status, stakeholder brief, replanning, and feature report artifacts. Canonical names and paths are defined in [references/canonical-paths.md](references/canonical-paths.md) and [references/contracts.md](references/contracts.md).
