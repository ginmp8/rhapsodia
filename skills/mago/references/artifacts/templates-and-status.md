# Templates and Status

Execution-oriented headings, metadata, and lifecycle values are downstream planning contracts; they do not make MAGO an execution skill.

## Template Use

Use `assets/templates/` through scripts whenever possible: `scripts/create_planning_identity.py` for cycle/registry identity, `scripts/write_artifact_scaffold.py` for package files, `scripts/update_template_lists.py` for supported list fields, `scripts/normalize_package.py` for bounded normalization, and artifact/package validators for checks.

Placeholders and examples are non-authoritative until reconciled with the selected registry record, package evidence, and repository truth. Before populating list fields, inspect `scripts/update_template_lists.py --schema --artifact-name <artifact>`.

The catalog and define-queue templates document renderer output only. They must describe the full item schema but must never be copied into canonical board state.

## Cross-Skill Template Boundary

MAGO owns canonical planning templates for cycle/registry identity and package planning files. MAGIA must not maintain duplicate planning templates or create replacement planning scaffolds. It may update only evidence-backed execution fields and existing task checkboxes.

## Canonical Artifact Invariants

Do not remove canonical structure unless replacing it with the canonical equivalent.

- `cycle.yaml`: keep immutable identity, board/year, creation metadata, lifecycle, planning revision, and optional delivery-version metadata.
- `registry/<spec_id>.yaml`: keep immutable identity, feature metadata, status, priority/order hint, dependencies, supersession, handoff, and import traceability.
- generated `spec-catalog.yaml`: keep kind/generated/cycle/digest fields and the full per-spec projection shape documented by its template.
- generated `define-queue.yaml`: keep kind/generated/cycle/digest fields and the full handoff projection shape documented by its template.
- `manifest.yaml`: keep identity, classification, planning status/phase, source-of-truth links, traceability, and evidence-backed `last_execution` only when it exists.
- `prd.md`: keep front matter and canonical sections unless a mode adds a truthful section.
- `technical-design.md`: keep architecture-focused content without implementation code or operational runbooks.
- `tasks.md`: keep H1, `Execution Rules`, five canonical phases in order, stable `taskNNN` checkbox lines, and canonical metadata fields.
- `validation.md`: keep strategy, scope, performance validation, and final verification checklist.
- `notes.md`: keep planning assumptions, repository findings, decisions, risks, trade-offs, open questions, and specialist rationale. New execution history belongs in MAGIA-owned files.
- drift reconciliation restores missing structure conservatively; it does not silently drop it.

## Canonical Task Contract

- Keep exactly five canonical phases in order: Foundation; Core Implementation; Integration; Validation and Hardening; Migration and Rollout.
- Every phase has at least one bounded truthful task. When no product change is required, add a `confirmation` task rather than leaving the phase empty.
- Minimum obligations: Phase 1 prerequisites/current boundary/context; Phase 2 main behavior/artifact/code path; Phase 3 integration or truthful no-extra-integration confirmation; Phase 4 correctness proof plus hardening/failure modes; Phase 5 adoption/operator docs/migration/rollout or truthful no-op confirmation.
- Use stable global `taskNNN`; never restart numbering by phase.
- Each actionable task declares `Objective`, `Affected boundary`, `Task type`, `Reasoning`, `Why this reasoning is sufficient`, `Specialist Support`, `Required LOAD`, `Optional LOAD`, `Selection Hint`, `Dependencies`, `Validation`, and `Expected result`.
- `Dependencies` references existing task IDs exactly.
- `Reasoning`: `low`, `medium`, `high`, `xhigh`; default to `low` or `medium`.
- Task type by phase: Phase 1 `analysis|setup|confirmation|refinement`; Phase 2 `implementation|refinement`; Phase 3 `integration|confirmation|refinement`; Phase 4 `validation|hardening|confirmation|refinement`; Phase 5 `migration|rollout|confirmation`.
- Use `refinement` only for bounded planning changes inside the same spec.
- Specialist selection is sparse, evidence-based, and aligned with `references/specialist-spellbook.md`.
- Normal target: 5–9 executable tasks, usually 1–3 per phase. If more than 12 remain after decomposition, split the work into another registered spec.

## Refinement Rules

Preserve truthful content, stable IDs, completed-task history, and cross-artifact references. Normalize conservatively; replace placeholders with real values; never copy example identity/status values blindly. A new material delivery wave is a new registry/spec package, not another phase cycle inside an existing package.

## Execution Handoff Consistency

MAGO may define downstream execution tasks and handoff expectations without becoming the executor. do not mark a task blocked merely because it requires downstream Magia implementation; block only for missing scope, files, dependencies, credentials, evidence, or validation paths. Keep runtime results in MAGIA-owned evidence artifacts.

## Cross-Artifact Consistency

- cycle, registry, package directory, and manifest identities must agree;
- active feature keys are unique unless supersession is explicit;
- spec dependencies resolve and remain acyclic;
- task IDs referenced by dependencies or execution evidence exist in `tasks.md`;
- `manifest.yaml.last_execution` contains only fields supported by current MAGIA evidence;
- registry and manifest planning/execution status changes are evidence-backed;
- generated views reproduce the registry but are never authoritative;
- auxiliary docs may clarify but must not replace canonical files.

## State Synchronization

Update state only from repository truth or recorded execution evidence; never simulate start, completion, or validation.

- Planning definition: registry `status: planned`; manifest `status: planned`; manifest `phase: define`.
- Truthful execution started: MAGIA may synchronize registry/manifest to `in_progress` and manifest phase to `execute`.
- Truthful completion: MAGIA may synchronize registry/manifest to `done` and phase to `done` only when required tasks are complete and matching validation evidence exists.
