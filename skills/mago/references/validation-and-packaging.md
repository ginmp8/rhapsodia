# MAGO Validation and Packaging

Load during MAGO hardening, package validation, or artifact edits needing mechanical validation.

## Artifact Validation Routing

Default validator: `scripts/validate_artifact.py`; it dispatches by path/name. Use narrower validators when target is known:

- `scripts/validate_package.py`: package under active board root.
- `scripts/validate_repo_board.py`: board placement, placeholders, cross-package quality.
- `scripts/validate_technical_design.py`: spec architecture artifacts.
- `scripts/validate_boundary.py`: package edits that may blur planning/governance/execution.
- `scripts/validate_activation_scenarios.py`: hardening/package validation for activation, ambiguity, refusal, regression, adversarial routing.
- `scripts/validate_evidence_contract.py`: evidence/traceability checks for repository truth, execution state, validation state, dependency state, or source-of-truth paths.
- `scripts/validate_skill_package.py`: MAGO package integrity before packaging; also gates activation metrics and evidence controls.
- `scripts/package_skill.py`: build `skill.zip` after folder validation and validate produced archive.

## Validation Gates

A MAGO run is incomplete until relevant gates are known: canonical board root resolved; touched artifacts remain inside it; template-backed artifacts have no unresolved dynamic placeholders unless explicitly scaffolded; package ids, task ids, dependencies, status fields, and specialist metadata are consistent; repository-board validation passes when board artifacts changed; failures are blockers, not success.

## Package-Level Hardening Gates

Before distributing MAGO:

1. Run static hardening audit if available.
2. Run `scripts/validate_activation_scenarios.py` against skill root with `examples/activation-scenarios.json` as deterministic oracle.
3. Run the skill-harness validator so `evals/activation-scenarios.json` stays schema-valid planned prompt-review coverage.
4. Run `scripts/validate_skill_package.py` against skill root.
5. Run `scripts/validate_boundary.py` from skill root.
6. Run or smoke-test `scripts/validate_evidence_contract.py` against a representative local package fixture when evidence controls changed.
7. Compile/smoke-test Python scripts without external services.
8. Run `python3 -S scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate`.
9. Verify archive has exactly one top-level skill directory containing `SKILL.md`, excludes transient reports/caches, and passes archive validator.

## Packaging Exclusions

Exclude transient reports, caches, virtual environments, bytecode caches, benchmark outputs, secrets, local credentials, and test-result files. The zip must contain one top-level skill directory with `SKILL.md`; do not package loose files at archive root.
