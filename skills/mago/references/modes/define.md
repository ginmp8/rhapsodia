# Define Mode

## Canonical Rules

- `BOARD_ROOT` is required for package traceability.
- The selected spec package path is always under `BOARD_ROOT/specs/<spec_id>/`.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; derive the selected package path from the canonical pattern for the selected spec package.
- Write package artifacts only under `BOARD_ROOT/specs/<spec_id>/`.

## Definition Workflow

1. Select exactly one spec from the active catalog.
2. Load only the selected spec package, relevant discovery evidence, and directly relevant repository code or tests.
3. When a define-queue.yaml handoff exists, preserve its truthful package shape, source mapping, and seeded artifacts unless current evidence proves they are wrong.
4. Open [../specialist-spellbook.md](references/specialist-spellbook.md) before writing or correcting task specialist metadata.
5. Create or refine manifest.yaml, prd.md, tasks.md, validation.md, and notes.md. Create technical-design.md only when the selected spec needs explicit architecture or contract alignment.
6. Keep the package aligned with the active catalog.
7. Apply [../markdown-writing.md](references/markdown-writing.md) to every changed Markdown artifact.
8. Finish with final review.

## Package Contract

- every execution-ready full package must contain at least the canonical files manifest.yaml, prd.md, tasks.md, validation.md, and notes.md
- full packages may also contain technical-design.md when architecture decisions, API/data contracts, migrations, security posture, monitoring, rollback, or external integrations need a separate design surface
- auxiliary spec-local docs may exist when they clarify the same spec root without replacing canonical files
- create every missing required file before treating the package as execution-ready
- keep each file aligned with the active catalog, selected spec identity, and repository truth

## Artifact Rules

- use templates only through local scripts when writing, refreshing, normalizing, or validating template-backed artifacts
- create missing template-backed files with scripts/write_artifact_scaffold.py <artifact-path> before filling repository-truth values
- replace all placeholders and example values with selected-spec and repository-truth values
- preserve truthful established values from the active catalog and selected package
- never copy dynamic values such as `cycle_version`, `order`, `spec_id`, `feature_version`, `type`, `classification`, `status`, or `phase` blindly from template text
- never copy suggested `Reasoning`, `Why this reasoning is sufficient`, `Specialist Support`, `Dependencies`, or `Task type` values blindly from template text
- if a required value is not yet justified by evidence, resolve it conservatively from the active catalog or record the uncertainty in notes.md instead of inventing a literal

## manifest.yaml

- required fields: `schema_version`, `spec_id`, `feature_key`, `title`, `type`, `classification`, `status`, `phase`, `cycle_version`, `feature_version`, `source_of_truth`, `traceability`
- optional field: `last_execution` after a task has truthfully executed
- planning-only definition normally keeps `status: planned` and `phase: define`
- keep `source_of_truth` paths lowercase
- preserve discovery traceability when applicable

## prd.md

- include the YAML metadata block for the selected spec
- cover: `Context`, `Problem Statement`, `Goals`, `Non-Goals`, `Current State`, `Proposed Outcome`, `Functional Requirements`, `Non-Functional Requirements`, `Constraints`, `Risks and Trade-Offs`, `Acceptance Criteria`, `Open Questions`
- be concrete and repository-aware
- keep acceptance criteria testable
- do not turn the PRD into a task list

## technical-design.md

- create only when architecture or contract detail would materially improve execution readiness
- cover context, problem, scope, technical solution, architecture decisions, security, testing, monitoring, rollback, risks, implementation approach, and open questions
- keep API contracts, data schemas, component responsibilities, and diagrams high-level
- do not include implementation code, CLI commands, deployment runbooks, task checklists, or claimed execution evidence
- keep detailed executable decomposition in tasks.md

## tasks.md

- follow the canonical tasks.md contract in [../artifacts/templates-and-status.md](references/artifacts/templates-and-status.md) for phase structure, task fields, allowed enums, task-count guidance, and cross-artifact consistency
- satisfy the canonical minimum phase coverage there before adding optional extra tasks
- in define mode, create or normalize the full five-phase sequence from scratch
- every phase still needs at least one bounded truthful task; use `confirmation` when a phase needs a real no-op proof, and use `refinement` only for bounded docs-only replanning inside the same spec root
- keep tasks small, concrete, and reviewable; split vague umbrella tasks before raising reasoning
- if the selected spec is already materially complete and new work represents a new material delivery slice, correction wave, or semantic evolution, create a new spec instead of reopening the phase structure with another cycle

## validation.md

- record only proof expectations relevant to the selected spec, such as compile-time, runtime, integration, regression, edge-case, backward-compatibility, performance, observability, and docs-consistency checks

## notes.md

- keep the canonical top-level sections from the template, even when a section is brief
- keep notes.md factual: assumptions, findings, decisions, risks, trade-offs, open questions, specialist rationale when used, and execution log
- in full-package define, keep the `Execution Log` heading present; add or preserve per-task subsections only when truthful execution history already exists
- when a task subsection exists, use the canonical fields `Status`, `Summary`, `Changes`, `Context Docs`, `Decisions`, `Follow-Ups`, and `Blockers`
- keep `Context Docs` repository-relative POSIX and use `none` when a required execution-log field is intentionally empty

## Final Review

- review order: manifest.yaml, prd.md, technical-design.md when present, validation.md, notes.md, then architecture impact when the selected spec changes public contracts, shared abstractions, runtime topology, persistence shape, or cross-package boundaries
- close only gaps that can already be resolved from current evidence
- keep all planning docs internally consistent
- add only the minimum new in-scope tasks required
- do not claim completion without evidence
