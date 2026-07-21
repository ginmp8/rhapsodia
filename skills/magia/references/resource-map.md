# Resource Map

Use to locate MAGIA resources without loading every file.

## Core References

- `references/board-contract.md`: self-contained canonical board, registry, identity, dependency, and execution-sync contract.

- `references/common-execution.md`: shared execution rules.
- `references/execution-entry.md`: compact start card, first-safe-action rules, bounded ambiguity handling, and concise completion view.
- `references/repository-orientation.md`: read-only brownfield orientation, repository signals, and orientation-to-execution gates.
- `references/senior-engineering-discipline.md`: small, explicit, verifiable engineering behavior.
- `references/risk-and-change-escalation.md`: standard/governed risk profiles, evidence precedence, contract-change controls, and closure gates.
- `references/safe-parallelism.md`: explicit execution-wave prerequisites, conflict rules, sequential fallback, and reconciliation gates.
- `references/complexity-reduction-execution.md`: behavior-preserving simplification, de-abstraction, refactor execution.
- `references/planning-handoff.md`: consume Mago/nomia artifacts, including execution-handoff-plan.md, as execution inputs.
- `references/developer-artifact-standards.md`: implementation-doc taxonomy/templates.
- `references/technical-documentation.md`: implementation ADR and doc rules.
- `references/validation-selection.md`: risk-based proof-category selection with explicit unavailable-check handling.
- `references/validation-and-closure.md`: truthful validation/closure.
- `references/execution-visibility-and-recovery.md`: non-authoritative execution-state projection and safe recovery decisions.
- `references/markdown-writing.md`: durable Markdown quality.
- `references/quickstarts.md`: onboarding for ADHOC, RALPH, ADAPT, validation, governed examples, blocked handoffs, and recovery.
- `references/package-delivery.md`: package MAGIA itself.

## Mode References

- `references/modes/adhoc.md`: direct repository work.
- `references/modes/ralph.md`: selected board/spec package execution.
- `references/modes/adapt.md`: best-effort conversion of legacy execution records into current MAGIA-owned artifacts.

## Artifact References

- `references/artifacts/execution-records.md`: controlled state sync.
- `references/artifacts/execution-evidence.md`: structured downstream evidence.

## Agent Metadata and Assets

- `agents/openai.yaml`: ChatGPT/Codex/API/Atlas metadata and activation defaults.
- `assets/icon.svg`: icon consumed by `agents/openai.yaml`; it is an asset, not reasoning context.

## Examples and Evaluations

- `examples/activation-scenarios.json`: human-readable calibration cases.
- `evals/activation-scenarios.json`: canonical planned activation, non-activation, ambiguous, edge, regression, and adversarial coverage. Metrics remain unmeasured until prompt outputs and evaluator decisions are captured.

## Templates

MAGIA-owned execution evidence templates: `assets/templates/implementation-notes.md.template`, `assets/templates/validation-evidence.md.template`, and `assets/templates/technical-gap-note.md.template`. MAGIA intentionally does not bundle templates for MAGO-owned planning artifacts (`registry/<spec_id>.yaml`, `manifest.yaml`, `tasks.md`, `notes.md`, or `validation.md`). Use MAGO to create or normalize those files, then use MAGIA execution-state scripts only to update existing records from truthful execution evidence.

Developer docs: `assets/templates/implementation-notes.md.template`, `assets/templates/complexity-reduction-evidence.md.template`, `assets/templates/implementation-adr.md.template`, `assets/templates/validation-evidence.md.template`, `assets/templates/runbook.md.template`, `assets/templates/migration-execution-note.md.template`, `assets/templates/contract-change-note.md.template`, `assets/templates/observability-note.md.template`, `assets/templates/troubleshooting.md.template`, `assets/templates/security-risk-note.md.template`, `assets/templates/technical-gap-note.md.template`.

## Scripts

- `scripts/inspect_repository_context.py`: produce a deterministic read-only JSON or Markdown orientation view without executing repository commands.
- `scripts/analyze_execution_waves.py`: conservatively classify explicit task graphs into parallel-safe or sequential waves without executing or mutating tasks.
- `scripts/select_validation_checks.py`: map explicit change surfaces to required and recommended validation categories without running checks.
- `scripts/summarize_execution_state.py`: produce a read-only execution and recovery projection without mutating state or running recovery.
- `scripts/write_artifact_scaffold.py`: copy a matching MAGIA-owned template only inside a validated `--board-root` or explicit ADHOC `--allowed-root`; it must not scaffold or update MAGO-owned planning files.
- `scripts/write_execution_log.py`: write execution logs.
- `scripts/adapt_legacy_execution_records.py`: convert legacy notes.md/validation.md execution content into current MAGIA-owned artifacts.
- `scripts/sync_execution_state.py`, `scripts/heal_execution_state.py`, `scripts/close_execution_state.py`: sync controlled execution records.
- `scripts/validate_artifact.py`, `scripts/validate_execution_state.py`, `scripts/validate_repo_board.py`, `scripts/validate_boundary.py`: validate artifacts/boundaries.
- `scripts/board_contract.py`: import-only canonical board parser consumed by board, readiness, state, and repository validators.
- `scripts/validate_board_contract.py`: validate canonical cycle, registry, dependencies, and manifest identity without loading another skill.
- `scripts/planning_traceability.py`: import-only parser for canonical planning anchors, legacy semantic linkage, task order, and Traceability source resolution; consumed by readiness and state validators.
- `scripts/validate_execution_readiness.py`: validate selected spec/task readiness, task-to-intent/check linkage, task order, and dependency completion.
- `scripts/validate_instruction_contract.py`: validate preservation of mandatory MAGIA instruction and ownership terms.
- `scripts/validate_planning_handoff_contract.py`: validate planning-origin execution and blocker rules after handoff-rule edits.
- `scripts/magia_utils.py`: import-only helper module used by execution-state, boundary, board, and log scripts; it has no standalone CLI by design.
- `scripts/package_policy.py`: import-only common archive candidate/exclusion and sensitive-name policy consumed by package validation and building.
- `scripts/security_scan.py`: import-only fail-closed content scanner consumed by package validation and building.
- `scripts/validate_skill_package.py`, `scripts/package_skill.py`: validate and package the same package-eligible candidate set.
