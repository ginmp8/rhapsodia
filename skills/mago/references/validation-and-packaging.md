# MAGO Validation and Packaging

Use this reference during MAGO hardening, package validation, or when a normal MAGO run touches artifacts that require mechanical validation.

## Artifact Validation Routing

Use `scripts/validate_artifact.py` as the default final validator for specific artifacts. It dispatches to the narrower validator based on the artifact path and file name.

Use narrower validators directly when the target is already known:

- `scripts/validate_package.py` for a package under the active board root.
- `scripts/validate_repo_board.py` for board-level placement, placeholders, and cross-package board quality.
- `scripts/validate_technical_design.py` for spec-scoped architecture artifacts.
- `scripts/validate_boundary.py` after package edits that could blur planning, governance, and execution boundaries.
- `scripts/validate_activation_scenarios.py` during hardening or package validation when activation, ambiguity, refusal, regression, or adversarial behavior needs measurable scenario evidence.
- `scripts/validate_evidence_contract.py` for package evidence and traceability checks when planning claims depend on repository truth, execution state, validation state, dependency state, or source-of-truth paths.
- `scripts/validate_skill_package.py` before packaging the MAGO skill itself; it also gates activation scenario metrics and package-level evidence controls.

## Validation Gates

A MAGO run is not complete until the relevant gates are known:

- canonical board root resolved;
- touched artifacts remain inside the resolved board root;
- template-backed artifacts have no unresolved dynamic placeholder values unless the mode explicitly creates a scaffold;
- package ids, task ids, dependencies, status fields, and specialist metadata are consistent;
- repository-board validation passes when board-level artifacts changed;
- failures are reported as blockers, not reframed as success.

## Package-Level Hardening Gates

Before distributing the MAGO skill package:

1. run a static hardening audit if available;
2. run `scripts/validate_activation_scenarios.py` against the skill root;
3. run `scripts/validate_skill_package.py` against the skill root;
4. run `scripts/validate_boundary.py` from the skill root;
5. run or smoke-test `scripts/validate_evidence_contract.py` against a representative local package fixture when evidence controls changed;
6. compile or smoke-test Python scripts without importing external services;
7. create the zip from the skill folder contents, not from a parent directory;
8. test the zip archive and validate an extracted copy.

## Packaging Exclusions

Do not include transient report folders, caches, virtual environments, bytecode caches, benchmark outputs, secrets, local credentials, or test-result files in the distributable package.

The zip should open with `SKILL.md` at archive root.
