# MAGO Validation and Packaging

Load during MAGO hardening, package validation, or artifact edits needing mechanical validation.

## Artifact Validation Routing

Default validator: `scripts/validate_artifact.py`; it dispatches by path/name. Use narrower validators when target is known:

- `scripts/validate_package.py`: package under the active board root.
- `scripts/validate_repo_board.py`: canonical board placement, unresolved tokens, discovery index, registry/identity rules, dependency DAG, package quality, technical design, and sibling-cycle conflicts.
- `scripts/validate_concurrent_board.py`: one resolved cycle root, including cycle/registry/package identity and semantic conflicts.
- `scripts/validate_generated_view_contract.py`: renderer and complete generated catalog/queue template schemas.
- `scripts/validate_technical_design.py`: spec architecture artifacts.
- `scripts/validate_plan_quality.py --require-v2`: new governed requirement criticality, risk-calibrated acceptance paths, alternatives, measurable NFRs, evidence capture, residual-risk disposition, and reproducible validation procedures; default mode remains legacy-readable.
- `scripts/validate_security_risk.py --require-v2`: relational security graph and authority checks for new governed security artifacts.
- `scripts/mutation_transaction.py`: executable staging, resume, drift, fault-injection, and verified rollback for multi-artifact planning writes.
- `scripts/sdd_adapter.py`: version-explicit Spec Kit/OpenSpec file projection and SHA-256 round-trip evidence.
- `scripts/validate_boundary.py`: package edits that may blur planning/governance/execution.
- `scripts/validate_activation_scenarios.py`: hardening/package validation for activation, ambiguity, refusal, regression, adversarial routing.
- `scripts/validate_evidence_contract.py`: evidence/traceability checks for repository truth, execution state, validation state, dependency state, or source-of-truth paths.
- `scripts/validate_planning_execution_handoff.py`: task/handoff language and planning-to-execution boundary.
- `scripts/validate_skill_package.py`: MAGO package integrity before packaging; also gates activation metrics, concurrency tests, generated-view contract, evidence controls, governed quality, security v2, executable adapter round trips, release metadata, and the full test suite.
- `scripts/run_sdd_evidence_harness.py`: isolated, bounded, machine-readable execution for deterministic quality, security, recovery, adapter, release, activation, and lifecycle scenarios. It defaults to reliable sequential execution, persists progress atomically, enforces per-scenario and whole-run deadlines, terminates process groups on interruption, and explicitly excludes live LLM claims.
- `scripts/run_test_suite.py`: isolated unittest-file runner with bounded shards, per-file and whole-suite deadlines, atomic checkpoints, signal-aware child cleanup, suite hashes, exact test counts, and machine-readable partial failure evidence.
- `scripts/merge_test_reports.py`: merges shard reports only when hashes match the current complete test suite, every test file appears exactly once, and all results pass.
- `scripts/validate_release_metadata.py`: version, changelog, compatibility, product declaration, installation, upgrade, rollback, and support-boundary checks.
- `scripts/validate_distribution.py`: one external gate for dependencies, release, activation, complete tests, core and lifecycle evidence, package validation, archive integrity, byte-equivalent extraction, and extracted-package revalidation.
- `scripts/package_skill.py`: build `skill.zip` after folder validation and validate the produced archive.

## Validation Gates

A MAGO run is incomplete until relevant gates are known: canonical board root resolved; cycle/spec IDs and year/path agree; touched artifacts remain inside the board/registry/package boundaries; template-backed artifacts have no unresolved dynamic placeholders unless explicitly scaffolded; package IDs, task IDs, dependencies, status fields, handoff fields, and specialist metadata are consistent; duplicate features and dependency cycles are absent; generated views are deterministic and external; repository-board validation passes when board artifacts changed; failures are blockers, not success.

## Generated View Validation

Render with `scripts/render_registry_views.py <board_root> --output <external-dir>`. Re-running unchanged input must produce byte-identical output and the same registry digest. Run `scripts/validate_generated_view_contract.py <skill-root>` whenever renderer logic or projection templates change. Generated views must not be placed under `BOARD_ROOT` or used as authoritative state.

## Package-Level Hardening Gates

For a complete distribution check, use one external command:

```bash
python -B scripts/validate_distribution.py \
  --target <skill-root> \
  --output-dir <external-output>/distribution \
  --report <external-output>/distribution-validation.json \
  --jobs 1
```

The command stops on the first failed gate and preserves an atomic JSON checkpoint. A passing report proves: declared runtime dependencies import; release and activation metadata validate; every current unittest file is represented by a hash-bound passing report; every core and lifecycle evidence scenario passes; package validation consumes the current test digest; the archive has one safe top-level `mago/` tree; extracted bytes match the validated source tree; and the extracted package passes dependency, release, and package validation again. It does not measure live model routing, prose quality, product runtime behavior, or business acceptance.

Individual validators remain available for diagnosis and sharding:

1. Run `scripts/validate_activation_scenarios.py` for the frozen static routing oracle.
2. Run `scripts/run_test_suite.py` and merge complete shards with `scripts/merge_test_reports.py`.
3. Run `scripts/run_sdd_evidence_harness.py` for `evidence/sdd-evidence-scenarios.json` and `evidence/lifecycle-contract-scenarios.json`; merge shards with `scripts/merge_evidence_reports.py`.
4. Pass the current merged test report to `scripts/validate_skill_package.py --test-report <report>`.
5. Build and validate `skill.zip` only after those gates pass.

## Packaging Exclusions

Exclude transient reports, generated catalog/queue outputs, caches, virtual environments, bytecode caches, benchmark outputs, secrets, local credentials, test-result files, temporary fixtures, and old archives. The zip must contain one top-level skill directory with `SKILL.md`; do not package loose files at archive root.
