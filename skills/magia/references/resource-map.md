# Resource Map

Use this reference when deciding which MAGIA support file, script, template, or scenario suite should be loaded or executed.

## Reference Files

| Resource | Load when |
|---|---|
| `references/canonical-paths.md` | Resolving board roots, selected spec packages, or canonical path ownership. |
| `references/common-execution.md` | Starting any ADHOC or RALPH execution run. |
| `references/modes/adhoc.md` | The request is a direct repository change not driven by a board contract. |
| `references/modes/ralph.md` | The request is driven by a concrete board contract and selected spec package. |
| `references/artifacts/execution-records.md` | Updating controlled execution artifacts, task state, validation records, notes, manifest state, or catalog state. |
| `references/artifacts/execution-evidence.md` | Emitting structured factual evidence for downstream consumption. |
| `references/validation-and-closure.md` | Closing any run that changed code, docs, evidence, task state, or execution state. |
| `references/markdown-writing.md` | Writing durable Markdown records such as notes and validation evidence. |
| `references/resource-map.md` | Auditing package resources, package validation, or selecting local MAGIA tooling. |
| `references/package-delivery.md` | Validating, exporting, or packaging the MAGIA skill itself. |

## Script Map

| Script | Purpose | Representative command shape |
|---|---|---|
| `scripts/write_artifact_scaffold.py` | Create a canonical artifact from its template-backed structure. | `python scripts/write_artifact_scaffold.py <artifact-path>` |
| `scripts/update_template_lists.py` | Populate supported list fields in template-backed artifacts from structured data. | `python scripts/update_template_lists.py <artifact-path> --data <payload.yaml>` |
| `scripts/validate_artifact.py` | Choose and run the correct artifact validator for a template-backed file. | `python scripts/validate_artifact.py <artifact-path>` |
| `scripts/write_execution_log.py` | Append or refresh a task execution-log subsection in notes. | `python scripts/write_execution_log.py <board-root> --spec-id <specNNN> --task-id <taskNNN> --status <status> --summary <summary>` |
| `scripts/close_execution_state.py` | Synchronize task state, validation evidence, notes, manifest state, and catalog state for truthful closure. | `python scripts/close_execution_state.py <board-root> --spec-id <specNNN> --task-id <taskNNN> --status <status>` |
| `scripts/heal_execution_state.py` | Repair narrow mechanical execution-state drift already supported by existing evidence. | `python scripts/heal_execution_state.py <board-root> --spec-id <specNNN>` |
| `scripts/sync_execution_state.py` | Fallback state synchronization when the closer is unavailable. | `python scripts/sync_execution_state.py <board-root> --spec-id <specNNN> --task-id <taskNNN> --status <status>` |
| `scripts/validate_execution_state.py` | Validate selected package execution-state consistency. | `python scripts/validate_execution_state.py <board-root> --spec-id <specNNN>` |
| `scripts/validate_repo_board.py` | Validate a repository board and selected cycle after RALPH execution. | `python scripts/validate_repo_board.py <repo-root> --board_id <board_id> --cycle_version <cycle_version>` |
| `scripts/validate_boundary.py` | Validate MAGIA ownership boundaries for created or changed durable docs. | `python scripts/validate_boundary.py <args>` |
| `scripts/package_skill.py` | Build `skill.zip` with one top-level skill directory and optional archive validation. | `python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate` |
| `scripts/validate_skill_package.py` | Validate the MAGIA skill package structure, links, placeholders, scripts, and optional zip artifact. | `python scripts/validate_skill_package.py --target <skill-root> --zip <skill.zip>` |

Use the local scripts before manual editing whenever they can perform the operation mechanically. If a script is missing an option needed for a template-backed field, extend the script first instead of hand-editing the structure.

## Template Map

| Template | Creates or normalizes |
|---|---|
| `assets/templates/spec-catalog.yaml.template` | Board-level spec catalog structure. |
| `assets/templates/manifest.yaml.template` | Selected spec package metadata and execution state. |
| `assets/templates/tasks.md.template` | Controlled task checklist and task metadata skeleton. |
| `assets/templates/notes.md.template` | Execution notes, logs, decisions, follow-ups, and blockers. |
| `assets/templates/validation.md.template` | Validation plan, evidence, checklist, and residual gaps. |

Templates are not examples. Treat them as machine-oriented inputs for scaffolding, population, and validation scripts.

## Scenario Suites

`examples/activation-scenarios.json` keeps the legacy human-readable activation plan. `evals/activation-scenarios.json` is the harness-readable planned scenario suite with activation, non-activation, ambiguity, edge-case, regression, and adversarial coverage. Use either as behavioral check plans only; do not report scenario metrics as measured unless the scenarios were actually executed and evaluator decisions were captured.

## Package Validation Gates

A MAGIA package is ready only when all applicable gates pass:

1. `SKILL.md` exists and frontmatter contains only lowercase `name` and lowercase `description`.
2. `SKILL.md` resolves every linked local reference or directory.
3. The package has references, scripts, templates, agent metadata, examples, and harness-readable eval scenarios when those resources are present in the workflow.
4. No scaffold placeholders remain outside templates.
5. Python scripts compile.
6. Optional zip validation confirms the archive contains exactly one top-level skill directory, excludes caches and blocked folders, and includes the expected package resources.
