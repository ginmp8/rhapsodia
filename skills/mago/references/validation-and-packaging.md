# MAGO Validation and Packaging

Load during MAGO hardening, package validation, or artifact edits needing mechanical validation.

## Artifact Validation Routing

Default validator: `scripts/validate_artifact.py`; it dispatches by path/name. Use narrower validators when target is known:

- `scripts/validate_package.py`: package under the active board root.
- `scripts/validate_repo_board.py`: canonical board placement, unresolved tokens, discovery index, registry/identity rules, dependency DAG, package quality, technical design, and sibling-cycle conflicts.
- `scripts/validate_concurrent_board.py`: one resolved cycle root, including cycle/registry/package identity and semantic conflicts.
- `scripts/validate_generated_view_contract.py`: renderer and complete generated catalog/queue template schemas.
- `scripts/validate_technical_design.py`: spec architecture artifacts.
- `scripts/validate_boundary.py`: package edits that may blur planning/governance/execution.
- `scripts/validate_activation_scenarios.py`: hardening/package validation for activation, ambiguity, refusal, regression, adversarial routing.
- `scripts/validate_evidence_contract.py`: evidence/traceability checks for repository truth, execution state, validation state, dependency state, or source-of-truth paths.
- `scripts/validate_planning_execution_handoff.py`: task/handoff language and planning-to-execution boundary.
- `scripts/validate_skill_package.py`: MAGO package integrity before packaging; also gates activation metrics, concurrency tests, generated-view contract, and evidence controls.
- `scripts/package_skill.py`: build `skill.zip` after folder validation and validate the produced archive.

## Validation Gates

A MAGO run is incomplete until relevant gates are known: canonical board root resolved; cycle/spec IDs and year/path agree; touched artifacts remain inside the board/registry/package boundaries; template-backed artifacts have no unresolved dynamic placeholders unless explicitly scaffolded; package IDs, task IDs, dependencies, status fields, handoff fields, and specialist metadata are consistent; duplicate active features and dependency cycles are absent; generated views are deterministic and external; repository-board validation passes when board artifacts changed; failures are blockers, not success.

## Generated View Validation

Render with `scripts/render_registry_views.py <board_root> --output <external-dir>`. Re-running unchanged input must produce byte-identical output and the same registry digest. Run `scripts/validate_generated_view_contract.py <skill-root>` whenever renderer logic or projection templates change. Generated views must not be placed under `BOARD_ROOT` or used as authoritative state.

## Package-Level Hardening Gates

Before distributing MAGO:

1. Run static hardening audit if available.
2. Run `scripts/validate_activation_scenarios.py` against the skill root with `examples/activation-scenarios.json` as deterministic oracle.
3. Run the skill-harness validator so `evals/activation-scenarios.json` stays schema-valid planned prompt-review coverage.
4. Run `scripts/validate_skill_package.py` against the skill root.
5. Run `scripts/validate_planning_execution_handoff.py` against the skill root.
6. Run `scripts/validate_generated_view_contract.py` against the skill root.
7. Run `scripts/validate_boundary.py` from the skill root.
8. Run or smoke-test `scripts/validate_evidence_contract.py` against a representative local package fixture when evidence controls changed.
9. Run the concurrency/unit test suite and a representative create/register/render/validate fixture.
10. Compile/smoke-test Python scripts without creating bytecode caches inside the skill.
11. Run `python3 -B scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate`.
12. Verify the archive has exactly one top-level `mago/` directory containing `SKILL.md`, excludes transient reports/caches, and passes folder/archive/extracted validation.

## Packaging Exclusions

Exclude transient reports, generated catalog/queue outputs, caches, virtual environments, bytecode caches, benchmark outputs, secrets, local credentials, test-result files, temporary fixtures, and old archives. The zip must contain one top-level skill directory with `SKILL.md`; do not package loose files at archive root.
