# Canonical Paths

Single source for canonical path definitions and override resolution.

## Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<cycle_version>/`
- Spec packages live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`.

## Resolution

- `BOARD_ROOT` is the active board root.
- If prompt provides `BOARD_ROOT`, use it only after validating against repository truth.
- Otherwise derive `BOARD_ROOT` from `CANONICAL_BOARD_ROOT` with concrete `board_id` and `cycle_version`.
- For spec-scoped work, derive the selected package from `BOARD_ROOT/specs/<spec_id>/`.
- Treat all other canonical paths as derived from `BOARD_ROOT`.

## Required Inputs

- `board_id` and `cycle_version`: required to derive `BOARD_ROOT`.
- `spec_id`: required for one selected spec package.
- If explicit `BOARD_ROOT` conflicts with dynamic ids or repository truth, stop instead of guessing.
