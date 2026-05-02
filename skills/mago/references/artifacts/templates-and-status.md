# Templates and Status

Execution-oriented headings, metadata, and lifecycle values are downstream planning contracts; they do not make MAGO an execution skill.

## Template Use

Use `assets/templates/` through scripts whenever possible: `scripts/write_artifact_scaffold.py` for template-backed writes, `scripts/update_template_lists.py` for supported list fields, `scripts/normalize_package.py` for safe package normalization, and `scripts/validate_artifact.py` or narrower validators for checks. Placeholders/examples are non-authoritative until reconciled with selected spec, active catalog, and repository truth.

After creating or editing a template-backed artifact, run `scripts/validate_artifact.py <artifact-path>`. Before list-field population, inspect `scripts/update_template_lists.py --schema --artifact-name <artifact>`; extend the script first if a needed list shape is unsupported.

Use only templates for files being created/normalized: spec-catalog.yaml, manifest.yaml, prd.md, technical-design.md, tasks.md, validation.md, notes.md.

## Canonical Artifact Invariants

Do not remove canonical structure unless replacing it with the canonical equivalent.

- spec-catalog.yaml: keep `schema_version`, `cycle_version`, `cycle_status`, `specs`; per spec keep `order`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `depends_on_features`, `depends_on_specs`, `status`, `feature_version`.
- manifest.yaml: keep template field set/order, including `schema_version`, identity fields, `status`, `phase`, `source_of_truth`, `traceability`; keep `last_execution` only when execution truth exists, with required `task_id` and optional `date`, `summary`, `files_changed`.
- prd.md: keep YAML front matter and canonical sections unless a mode adds a truthful extra section.
- technical-design.md: keep YAML front matter and canonical sections; keep architecture-focused, without implementation code fences or CLI runbooks.
- tasks.md: keep H1, `Execution Rules`, five canonical phase headings in order, stable `taskNNN` checkbox lines, and all canonical task metadata fields.
- validation.md: keep H1, `Validation Strategy`, `Validation Scope`, `Performance Validation`, `Final Verification Checklist`.
- notes.md: full-package modes keep canonical top-level sections. Product-only modes keep product-relevant sections unless truthful execution sections already exist. Executed task subsections under `Execution Log` keep `Status`, `Summary`, `Changes`, `Context Docs`, `Decisions`, `Follow-Ups`, `Blockers`; `Status` only `not_started`, `in_progress`, `blocked`, `done`.
- Drift reconciliation restores missing canonical structure conservatively; it does not silently drop it.

## Canonical Task Contract

- Use exactly this phase order: `Phase 1 - Foundation`, `Phase 2 - Core Implementation`, `Phase 3 - Integration`, `Phase 4 - Validation and Hardening`, `Phase 5 - Migration and Rollout`.
- Every phase has `Goal`, `Exit Criteria`, and at least one bounded truthful task.
- Minimum obligations: Phase 1 prerequisites/current boundary/context; Phase 2 main behavior/artifact/code path; Phase 3 required integration or truthful no-extra-integration confirmation; Phase 4 correctness proof plus hardening/failure-mode coverage; Phase 5 adoption/operator docs/migration or truthful no-rollout confirmation.
- If a phase has no product change, add a bounded `confirmation` task; never leave it empty.
- Use stable global `taskNNN`; do not restart numbering per phase.
- Actionable tasks declare `Objective`, `Affected boundary`, `Task type`, `Reasoning`, `Why this reasoning is sufficient`, `Specialist Support`, `Required LOAD`, `Optional LOAD`, `Selection Hint`, `Validation`, `Expected result`, `Dependencies`.
- `Dependencies` reference existing `taskNNN` ids exactly.
- `Reasoning`: `low`, `medium`, `high`, `xhigh`; default `low`/`medium`.
- `Task type` by phase: Phase 1 `analysis|setup|confirmation|refinement`; Phase 2 `implementation|refinement`; Phase 3 `integration|confirmation|refinement`; Phase 4 `validation|hardening|confirmation|refinement`; Phase 5 `migration|rollout|confirmation`.
- Use `refinement` only for bounded docs-only replanning inside the same spec root.
- Specialist selection is mandatory, sparse, and aligned with [../specialist-spellbook.md](../specialist-spellbook.md).
- Normal spec target: `5` to `9` executable tasks, usually `1` to `3` per phase. If more than `12` remain after decomposition, split into another spec.

## Refinement Rules

When refining: preserve truthful content; normalize conservatively; replace placeholders with real values; never copy dynamic template values or suggested metadata blindly; keep heading readability, lowercase YAML keys, and one canonical five-phase tasks.md with at least one bounded truthful task per phase; preserve minimum phase coverage; preserve existing task/checklist positions unless repository truth requires structural correction; model a new material delivery wave as another spec, not another phase cycle; prefer `scripts/normalize_package.py <board_root> --spec-id <specNNN>` for mechanical legacy drift before final validation.

## Cross-Artifact Consistency

- `cycle_status`: `planned`, `in_progress`, `done`, `cancelled`.
- New catalog default: `cycle_version: 01.00.00`, `cycle_status: planned`, unless repository truth differs.
- `taskNNN` references in `Dependencies`, notes.md execution logs, and `manifest.yaml.last_execution.task_id` must exist in tasks.md.
- `manifest.yaml.last_execution`: required `task_id`; optional `date`, `summary`, `files_changed`; preserve truthful legacy extra keys, do not invent new noncanonical keys.
- Keep `Execution Log` empty/minimal until truthful execution; use `none` for intentionally empty required execution-log fields; omit `manifest.yaml.last_execution` until truthful execution.
- If touched spec root includes tasks.md, run `scripts/validate_package.py` when available. Run `scripts/validate_repo_board.py` for resolved board root when available.
- Auxiliary spec-local docs may exist but must not replace or contradict canonical package files.
- technical-design.md is canonical optional spec-local artifact only when created through MAGO template and validator.

## State Synchronization

Update state only from repository truth or recorded execution evidence; never simulate start, completion, or validation.

- Planning-only definition: catalog `status: planned`; manifest `status: planned`; manifest `phase: define`.
- Truthful execution started: catalog `status: in_progress`; manifest `status: in_progress`; manifest `phase: execute`.
- Truthful completion: catalog `status: done`; manifest `status: done`; manifest `phase: done`; no required tasks left open; validation.md contains matching validation evidence.
