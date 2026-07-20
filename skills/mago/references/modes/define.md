# Define Mode

## Canonical Rules

`BOARD_ROOT` is required. The selected registry record is `BOARD_ROOT/registry/<spec_id>.yaml`; the selected package path is always `BOARD_ROOT/specs/<spec_id>/`. Prompt-provided `BOARD_ROOT` wins after validation. Write package artifacts only inside the selected package path and do not mutate unrelated registry records.

## Workflow

1. Select exactly one registered spec from the active cycle.
2. Load its registry record, package, relevant discovery evidence, and directly relevant repository code/tests.
3. Preserve truthful registry handoff package shape, source mapping, dependencies, and seeded artifacts unless current evidence proves them wrong.
4. Open `references/specialist-spellbook.md` before writing/correcting task specialist metadata.
5. Create/refine manifest.yaml, prd.md, tasks.md, validation.md, notes.md; create technical-design.md only for material architecture/contract alignment.
6. Keep package identity and planning fields aligned with cycle.yaml and the selected registry record.
7. Apply `references/markdown-writing.md` to changed Markdown.
8. Finish with final review and package/board validation.

## Package Contract

Execution-ready full packages contain manifest.yaml, prd.md, tasks.md, validation.md, notes.md, plus optional technical-design.md when architecture decisions, API/data contracts, migrations, security, monitoring, rollback, or external integrations need a separate design surface. Auxiliary spec-local docs may clarify the same root but cannot replace canonical files. Create missing required files before claiming execution readiness. Align every file with cycle metadata, registry identity, selected spec meaning, and repository truth.

## Artifact Rules

Use templates only through local scripts for writing, refresh, normalization, or validation. Create missing template-backed files with `scripts/write_artifact_scaffold.py <artifact-path>` before filling truth values. Replace all placeholders/examples. Preserve truthful registry/package values. Never blindly copy template dynamic fields (`cycle_id`, `spec_id`, `feature_version`, `type`, `classification`, `status`, `phase`, dependencies, priority, `order_hint`) or suggested task metadata (`Reasoning`, `Why this reasoning is sufficient`, `Specialist Support`, `Dependencies`, `Task type`). If evidence does not justify a required value, resolve from the selected registry record conservatively or record uncertainty in notes.md.

## Artifact Requirements

- manifest.yaml: required `kind`, `spec_id`, `spec_uid`, `cycle_id`, `feature_key`, `title`, `type`, `classification`, `status`, `phase`, `feature_version`, `created_at`, `source_of_truth`, `traceability`; optional truthful `last_execution`; planning-only usually `status: planned`, `phase: define`; keep `source_of_truth` paths lowercase and discovery traceability when applicable.
- prd.md: YAML metadata plus `Context`, `Problem Statement`, `Goals`, `Non-Goals`, `Current State`, `Proposed Outcome`, `Functional Requirements`, `Non-Functional Requirements`, `Constraints`, `Risks and Trade-Offs`, `Acceptance Criteria`, `Open Questions`. Be concrete, repository-aware, and testable; do not turn PRD into a task list.
- technical-design.md: create only when architecture/contract detail improves readiness. Cover context, problem, scope, solution, architecture decisions, security, testing, monitoring, rollback, risks, implementation approach, open questions. Keep contracts/schemas/responsibilities/diagrams high-level; no implementation code, CLI commands, deployment runbooks, task checklists, or claimed execution evidence.
- tasks.md: follow `references/artifacts/templates-and-status.md` for phase structure, fields, enums, task-count guidance, and consistency. Define mode creates/normalizes the full five-phase sequence. Every phase needs at least one bounded truthful task; use `confirmation` for real no-op proof and `refinement` only for bounded docs-only replanning inside the same spec root. Keep tasks small/reviewable; split vague umbrella tasks before raising reasoning. If materially complete work now needs a new slice/correction/evolution, create a new spec instead of reopening phases.
- validation.md: record only selected-spec proof expectations: compile-time, runtime, integration, regression, edge-case, backward-compatibility, performance, observability, docs consistency. Do not record executed command results here; MAGIA records those in validation-evidence.md.
- notes.md: keep canonical top-level planning sections. Include factual assumptions, findings, planning decisions, risks, trade-offs, open questions, and specialist rationale when used. Do not preserve legacy execution history as compatible planning content; MAGIA records current execution history in implementation-notes.md, and legacy execution sections must be adapted before use.

## Final Review

Review in order: registry record and manifest.yaml identity, prd.md, technical-design.md when present, validation.md, notes.md, then architecture impact when the spec changes public contracts, shared abstractions, runtime topology, persistence shape, or cross-package boundaries. Close only evidence-supported gaps, keep docs consistent, add only minimum in-scope tasks, and never claim completion without evidence.
