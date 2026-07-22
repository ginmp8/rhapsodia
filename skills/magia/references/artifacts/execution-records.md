# Execution Records

Load when execution updates tasks.md, registry/<spec_id>.yaml, manifest.yaml, validation-evidence.md, or implementation-notes.md.

## Ownership Boundary

- Records live under `BOARD_ROOT`; `board_id`, `year`, `cycle_id`, and selected `spec_id` must be concrete before reads/writes.
- prd.md is input. tasks.md is read-mostly; only toggle an existing checkbox when that task truthfully reached done.
- Do not create, refine, split, resequence, rewrite, or correct task prose, ids, order, dependencies, or metadata.
- If honest execution requires task-plan or metadata changes, stop and hand off to planning.
- Do not scaffold planning-owned artifacts from MAGIA. `cycle.yaml`, `registry/<spec_id>.yaml`, `tasks.md`, `manifest.yaml`, `notes.md`, and `validation.md` must already come from a planning package before MAGIA updates execution state.

## Planning-Origin Package Rules

- Treat planning fields as execution contract inputs; preserve fields/provenance while executing.
- Do not write execution logs that classify implementation requirement, roadmap/governance provenance, or pre-execution planned status as blockers.
- If an old log recorded that invalid blocker, do not repeat it as current truth; correct only when the task is re-executed or repaired with evidence.

## Canonical Structure

- `registry/<spec_id>.yaml`: preserve `kind`, `spec_id`, `cycle_id`, `feature_key`, `feature_version`, `title`, `type`, `classification`, `created_at`, `priority`, `order_hint`, dependency fields, supersession fields, handoff, and import provenance. MAGIA may update only evidence-backed technical execution `status`.
- manifest.yaml: preserve field set/order, including `kind`, immutable identity fields, `status`, `phase`, `feature_version`, `created_at`, `source_of_truth`, `traceability`, and optional last_execution. Canonical last_execution keeps `task_id` required and `date`, `summary`, `files_changed` optional.
- tasks.md: preserve phase headings, task order, task ids, metadata, and only toggle existing checkboxes for tasks completed in the current run.
- validation.md: read-only planning validation plan; preserve when encountered and do not append new runtime evidence.
- validation-evidence.md: preserve H1 and execution evidence sections; execution run headings identify taskNNN and optional date. A done task requires a concrete passed Executed Checks row plus a passed Traceability row linking a requirement, acceptance criterion, or task objective to that same executed check and its evidence. Meta-only, scaffold-marker, absent, or unrelated rows do not authorize completion.
- notes.md: read-only planning notes; do not preserve or read legacy Execution Log sections during normal execution. Convert them only through ADAPT mode when explicitly requested or required before execution.
- implementation-notes.md: preserve canonical top sections and Execution Log labels Status, Summary, Changes, Context Docs, Decisions, Follow-Ups, Blockers. Status values: not_started, in_progress, blocked, done; use none for intentionally empty fields.
- Generated catalog and queue projections are not active execution records and must never be updated by MAGIA.

## Writing Rules

Resource anchors: `assets/templates/` contains MAGIA-owned execution/doc templates only; `scripts/write_execution_log.py` is the canonical execution-log writer.

- For implementation-notes.md or validation-evidence.md edits, load `references/markdown-writing.md`.
- Create MAGIA-owned docs with `scripts/write_artifact_scaffold.py --board-root <board_root> <artifact-path>` or a narrower script; for ADHOC paths outside a board, require explicit `--allowed-root <root>`; do not use MAGIA to seed/refresh/normalize planning-owned files.
- Populate supported template lists with `scripts/update_template_lists.py <artifact-path> --data <payload.yaml>`; inspect shapes with `scripts/update_template_lists.py --schema --artifact-name <artifact>` and extend the script first if needed.
- Preserve headings, frontmatter keys, field labels, checklist/execution-log order, and truthful neighboring content.
- For implementation-notes.md Execution Log, use `scripts/write_execution_log.py <board_root> --spec-id <spec_id> --task-id <taskNNN> ...`; it keeps `## Execution Log` last, removes stale same-task copy, and appends the refreshed subsection.
- Never overwrite truthful dynamic values with placeholders or example literals.
- When completion state or records changed, use `scripts/close_execution_state.py` for semantic preflight, candidate validation, recoverable sync, and final validation. The recoverable sync validates journal entries against the three authorized execution-state files, blocks traversal/symlink escapes and live lock takeover, recovers dead-owner locks, and compares current source bytes with the preflight snapshot before replacement. Run `scripts/heal_execution_state.py` separately before closure only for previously evidenced narrow drift.
- Fall back to `scripts/sync_execution_state.py <board_root> --spec-id <spec_id> ...` plus `scripts/validate_execution_state.py <board_root> --spec-id <spec_id>` only when close wrapper is unavailable.
- Use `scripts/heal_execution_state.py <board_root> --spec-id <spec_id>` only for narrow mechanical reconciliation already proven by implementation-notes.md and validation-evidence.md; never invent validation, rewrite tasks, or repair task ids.
- Validate touched artifacts with `scripts/validate_artifact.py <artifact-path>` before closure.
- Run `scripts/validate_repo_board.py <repo_root> --board-root <board_root>` before closure when local repo files exist.
- Toggle tasks.md checkboxes in place. Do not toggle validation.md checklist items; write actual outcomes to validation-evidence.md.
- Update manifest.yaml last_execution only when a real task executed; otherwise preserve truthful existing value or omit it.

## Cross-Artifact Consistency

- Any taskNNN in implementation-notes.md Execution Log or `manifest.yaml.last_execution.task_id` must exist in tasks.md.
- Tasks completed in the current run must have existing tasks.md boxes checked before closure.
- Tasks recorded as executed in implementation-notes.md should have matching validation-evidence.md evidence.
- Preserve `manifest.yaml.last_execution` only when it is backed by current implementation-notes.md and validation-evidence.md evidence; otherwise adapt or clear/report the stale state.
- Registry filename, package directory, registry `spec_id`, and manifest `spec_id` must match.
- Immutable identity fields shared by registry and manifest must match.
- Registry status and manifest status must match after execution sync.
- If manifest.yaml or registry/<spec_id>.yaml is done, required tasks must not remain open in tasks.md.
- Do not duplicate execution evidence across noncanonical docs.
