# Templates and Status

Execution-oriented headings, metadata, and lifecycle values in these templates belong to the planning artifact contract consumed later by execution work. They do not change `mago` into an execution skill.

## Templates

Use templates under `assets/templates/` only through local scripts when any script can perform the operation. Use `scripts/write_artifact_scaffold.py` for template-backed writes, `scripts/update_template_lists.py` for supported list-field population, `scripts/normalize_package.py` for safe package normalization, and `scripts/validate_artifact.py` or a narrower validator for validation. Treat placeholders and example-like values as non-authoritative until reconciled with the selected spec, active catalog, and repository truth.

Validation rule: after creating or editing a template-backed MAGO artifact, run scripts/validate_artifact.py <artifact-path> so validator selection is mechanical rather than left to model judgment. Before populating any list field, check `scripts/update_template_lists.py --schema --artifact-name <artifact>` and extend that script first when a needed list shape is unsupported.

Use only the templates for files you are creating or normalizing:

- spec-catalog.yaml.template
- manifest.yaml.template
- prd.md.template
- technical-design.md.template
- tasks.md.template
- validation.md.template
- notes.md.template

## Canonical Artifact Invariants

Do not remove required canonical structure unless the same edit replaces it with the canonical equivalent.

- spec-catalog.yaml: preserve `schema_version`, `cycle_version`, `cycle_status`, and the `specs` sequence. Within each spec entry preserve `order`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `depends_on_features`, `depends_on_specs`, `status`, and `feature_version`.
- manifest.yaml: preserve the template field set and order, including `schema_version`, identity fields, `status`, `phase`, `source_of_truth`, and `traceability`; preserve `last_execution` only when execution truth exists, with `task_id` required and `date`, `summary`, and `files_changed` optional.
- prd.md: preserve the YAML front matter field set and the canonical section set unless the selected mode adds a truthful extra section.
- technical-design.md: preserve the YAML front matter field set and canonical section set; keep it architecture-focused and free of implementation code fences or CLI runbooks.
- tasks.md: preserve the H1, `Execution Rules`, the five canonical phase headings in order, stable `taskNNN` checkbox lines, and each task's metadata fields defined in the canonical task contract below.
- validation.md: preserve the H1, `Validation Strategy`, `Validation Scope`, `Performance Validation`, and `Final Verification Checklist`.
- notes.md: preserve the canonical top-level sections in full-package modes; in product-only modes keep only product-relevant sections unless truthful existing execution sections must be preserved. For every executed task subsection under `Execution Log`, preserve the field labels `Status`, `Summary`, `Changes`, `Context Docs`, `Decisions`, `Follow-Ups`, and `Blockers`, and use `Status` only from `not_started`, `in_progress`, `blocked`, or `done`.
- when reconciling drift, restore missing canonical structure conservatively instead of silently dropping it

## Canonical Task Contract

- keep exactly one canonical phase sequence in this order: `Phase 1 - Foundation`, `Phase 2 - Core Implementation`, `Phase 3 - Integration`, `Phase 4 - Validation and Hardening`, `Phase 5 - Migration and Rollout`
- every phase must include `Goal` and `Exit Criteria`
- every phase must contain at least one bounded, truthful task
- every phase must cover its canonical minimum obligation before optional extra tasks are added:
  - `Phase 1 - Foundation`: prerequisites, current boundary, and the context needed to start truthful implementation
  - `Phase 2 - Core Implementation`: the main behavior, artifact, or code path the spec exists to deliver
  - `Phase 3 - Integration`: required integration work, or a truthful confirmation that no additional integration is needed
  - `Phase 4 - Validation and Hardening`: proof of correctness plus the most important hardening or failure-mode coverage
  - `Phase 5 - Migration and Rollout`: adoption, operator docs, migration work, or a truthful confirmation that no additional rollout work is needed
- when a phase has no product change, use a bounded `confirmation` task instead of leaving the phase empty
- use stable global task ids in the form `taskNNN`; do not restart numbering per phase
- every actionable task must declare `Objective`, `Affected boundary`, `Task type`, `Reasoning`, `Why this reasoning is sufficient`, `Specialist Support`, `Required LOAD`, `Optional LOAD`, `Selection Hint`, `Validation`, `Expected result`, and `Dependencies`
- keep `Dependencies` referencing existing `taskNNN` ids exactly
- use `Reasoning` only from `low`, `medium`, `high`, `xhigh`; default to `low` or `medium`
- use `Task type` only from this phase-aligned enum mapping:
  - `Phase 1 - Foundation`: `analysis`, `setup`, `confirmation`, `refinement`
  - `Phase 2 - Core Implementation`: `implementation`, `refinement`
  - `Phase 3 - Integration`: `integration`, `confirmation`, `refinement`
  - `Phase 4 - Validation and Hardening`: `validation`, `hardening`, `confirmation`, `refinement`
  - `Phase 5 - Migration and Rollout`: `migration`, `rollout`, `confirmation`
- use `refinement` only for bounded docs-only replanning inside the same spec root
- specialist selection is mandatory on every task; keep it sparse and align it with [specialist-spellbook.md](references/specialist-spellbook.md)
- target `5` to `9` executable tasks for a normal spec and usually `1` to `3` executable tasks per phase
- if one spec still needs more than `12` executable tasks after decomposition, split the work into another spec instead of overloading the task list

When refining existing files:

- preserve truthful content and normalize conservatively
- replace every placeholder with real values; never copy dynamic template values or suggested task metadata blindly
- keep heading readability, YAML keys lowercase, and tasks.md in the single canonical five-phase order with at least one bounded truthful task per phase
- preserve the canonical minimum phase coverage even when the task list grows beyond the template's starter tasks
- preserve existing task and checklist line positions unless repository truth requires a structural correction
- represent a new material delivery wave as another spec, not another phase cycle
- when legacy execution-log or package-format drift can be normalized mechanically without inventing content, prefer `scripts/normalize_package.py <board_root> --spec-id <specNNN>` before the final validation pass

## Cross-Artifact Consistency

- use `cycle_status` only from `planned`, `in_progress`, `done`, or `cancelled`
- when bootstrapping a new catalog, use `cycle_version: 01.00.00` and `cycle_status: planned` unless repository truth already establishes another starting point
- any `taskNNN` referenced in `Dependencies`, notes.md execution-log subsections, or `manifest.yaml.last_execution.task_id` must exist in tasks.md
- canonical `manifest.yaml.last_execution` keeps `task_id` required and `date`, `summary`, and `files_changed` optional; preserve truthful legacy extra keys conservatively, but do not invent new noncanonical keys when defining or refining
- when a task has not executed yet, keep `Execution Log` empty or minimal; use `none` when a required execution-log field is intentionally empty
- omit `manifest.yaml.last_execution` until a task has truthfully executed
- when local `scripts/validate_package.py` exists and a touched spec root includes tasks.md, run it before closing to catch cross-artifact drift mechanically
- when local `scripts/validate_repo_board.py` exists, run it for the resolved board root before closing to catch noncanonical paths and unresolved placeholders
- auxiliary spec-local docs may exist, but they must not replace canonical package files or contradict them
- technical-design.md is a canonical optional spec-local artifact when created through the MAGO template and validator

## State Synchronization

Update these states only when repository truth or already-recorded execution evidence supports the transition. `mago` can reconcile truthful state; it must not simulate start, completion, or validation.

Planning-only definition normally means:

- catalog `status: planned`
- manifest `status: planned`
- manifest `phase: define`

When execution has truthfully started, states normally align as:

- catalog `status: in_progress`
- manifest `status: in_progress`
- manifest `phase: execute`

When execution is truthfully complete, completion normally requires:

- catalog `status: done`
- manifest `status: done`
- manifest `phase: done`
- no required work left open in tasks.md
- matching validation evidence in validation.md
