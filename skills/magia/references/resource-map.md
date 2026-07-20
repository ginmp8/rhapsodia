# MAGIA Resource Map

Load only resources required by the active source mode, execution profile, risk, artifact, or package operation. `SKILL.md` is the control plane; references carry branch detail; scripts perform deterministic work; templates define output structures; examples and evals calibrate behavior.

## Core Execution

- `references/canonical-paths.md`: canonical board and spec paths.
- `references/board-contract.md`: local board-contract semantics.
- `references/common-execution.md`: shared source-of-truth and editing rules.
- `references/senior-engineering-discipline.md`: non-trivial engineering discipline.
- `references/complexity-reduction-execution.md`: behavior-preserving simplification.
- `references/validation-and-closure.md`: final validation and record alignment.

## Modes and Profiles

- `references/modes/adhoc.md`: direct repository execution.
- `references/modes/ralph.md`: selected board/spec task execution.
- `references/modes/adapt.md`: legacy execution-record adaptation.
- `references/execution-profiles.md`: quick, standard, governed evidence and escalation.

## State, Convergence, Recovery

- `references/run-state-and-recovery.md`: checkpoints, fingerprints, resume, cancel, retry, rollback, handoff.
- `references/convergence-and-validation.md`: requirement-to-evidence statuses, risk matrix, evidence compression.
- `references/multi-repository-execution.md`: dependency order, compatibility windows, partial failure.
- `references/failure-recovery-taxonomy.md`: repair, retry, rollback, stop, and handoff categories.
- `scripts/run_state.py`: standalone run-state transition CLI.
- `scripts/select_validation.py`: deterministic minimum profile and check selector.
- `scripts/validate_convergence.py`: convergence JSON validator.

## Planning and External Inputs

- `references/planning-handoff.md`: planning-gap handoff and non-blockers.
- `references/shared-artifact-ownership.md`: Mago/Magia record ownership.
- `references/public-artifact-adapters.md`: read-only Spec Kit, Kiro, and OpenSpec mapping.
- `scripts/adapt_public_artifacts.py`: read-only normalization into an external JSON execution view.

## Execution Records and Evidence

- `references/artifacts/execution-records.md`: controlled task, manifest, registry, notes, and validation record rules.
- `references/artifacts/execution-evidence.md`: structured evidence for downstream consumers.
- `scripts/write_execution_log.py`: append implementation execution history.
- `scripts/sync_execution_state.py`: synchronize controlled state from current evidence.
- `scripts/heal_execution_state.py`: narrow mechanical healing of inconsistent execution state.
- `scripts/close_execution_state.py`: validated closure transition.
- `scripts/validate_execution_state.py`: cross-record consistency checks.

## Board and Repository Validation

- `scripts/board_contract.py`: import-only board-contract query helpers used by validators and execution scripts.
- `scripts/magia_utils.py`: import-only path, YAML, identity, and shared script helpers.
- `scripts/validate_board_contract.py`: board-contract validator.
- `scripts/validate_execution_readiness.py`: selected spec/task readiness gate.
- `scripts/validate_repo_board.py`: canonical repository-board structure validator.
- `scripts/validate_planning_handoff_contract.py`: planning handoff boundary validator.
- `scripts/validate_boundary.py`: self-containment, ownership, and forbidden downstream surface checks.
- `scripts/validate_instruction_contract.py`: instruction-depth and preserved-capability gate.

## Artifact Writing

- `references/developer-artifact-standards.md`: technical artifact quality rules.
- `references/technical-documentation.md`: execution-grounded documentation.
- `references/markdown-writing.md`: durable Markdown conventions.
- `scripts/write_artifact_scaffold.py`: template-backed MAGIA artifact creation.
- `scripts/update_template_lists.py`: narrow list updates for MAGIA-owned template-backed records.
- `scripts/validate_artifact.py`: artifact structure validation.
- `scripts/adapt_legacy_execution_records.py`: ADAPT conversion command.

## Templates

Human-readable templates under `assets/templates/`:

- implementation notes, validation evidence, technical gap, complexity reduction, implementation ADR;
- migration, contract, observability, runbook, troubleshooting, and security records.

Machine-readable templates:

- `assets/templates/run-state.json.template`;
- `assets/templates/execution-summary.json.template`;
- `assets/templates/convergence-report.json.template`.

Templates are copied or filled as outputs. Do not load every template as reasoning context.

## Scenarios and Tests

- `examples/activation-scenarios.json`: human-readable activation calibration.
- `evals/activation-scenarios.json`: target activation, boundary, regression, adversarial, recovery, and adapter coverage.
- `evals/booster-activation-scenarios.json`: deterministic four-category booster schema/coverage suite.
- `tests/test_board_contract.py`: board contract behavior.
- `tests/test_execution_flow.py`: execution record workflow.
- `tests/test_independence.py`: package independence and ownership.
- `tests/test_preserved_surface.py`: original resource and capability preservation.
- `tests/test_optimization_architecture.py`: profiles, state drift, convergence, and read-only adapter behavior.

## Package Delivery

- `references/package-delivery.md`: folder/archive validation and exclusions.
- `scripts/validate_skill_package.py`: complete package and optional archive validator.
- `scripts/package_skill.py`: deterministic complete `skill.zip` builder.

## Loading Discipline

1. Read `SKILL.md` first.
2. Load core execution and exactly one source mode.
3. Load execution profiles for every mutation.
4. Add state, convergence, recovery, multi-repository, adapter, or documentation resources only when triggered.
5. Prefer deterministic scripts over manual mutation for strict state, validation, adaptation, or packaging.
6. Keep board helpers import-only; do not add artificial CLIs merely to satisfy superficial resource checks.
7. Validate touched resources and package shape before readiness claims.
