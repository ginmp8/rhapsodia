# Canonical Paths

Single source for Magiarca path defaults and runtime root resolution.

## Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<cycle_version>/`
- Linked spec packages live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`.

## Resolution

- `BOARD_ROOT` is the active root for repository-facing Magiarca artifacts.
- Use prompt-provided `BOARD_ROOT` after validating repository truth; otherwise derive it from concrete `board_id` and `cycle_version`.
- Board-scoped artifacts derive from `BOARD_ROOT`.
- Spec-scoped artifacts derive from `BOARD_ROOT/specs/<spec_id>/`.
- Do not invent alternate governance roots or nested output roots.

## Dynamic Inputs

`board_id` and `cycle_version` are required to derive `BOARD_ROOT`; `spec_id` is required for spec-scoped writes. If explicit `BOARD_ROOT` conflicts with dynamic ids or repository truth, stop rather than guess.
