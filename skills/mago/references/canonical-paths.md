# Canonical Paths

Use this file as the single source of truth for canonical path definitions and override resolution.

## Canonical Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<cycle_version>/`
- spec packages always live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`

## Operational Resolution

- `BOARD_ROOT` is the active board root for the run.
- If the prompt provides `BOARD_ROOT`, use it after validating that it matches repository truth.
- Otherwise derive `BOARD_ROOT` from `CANONICAL_BOARD_ROOT` with concrete `board_id` and `cycle_version`.
- For spec-scoped planning, derive the selected spec package path from `BOARD_ROOT/specs/<spec_id>/`.
- Treat every other canonical file or directory path as derived from `BOARD_ROOT`.

## Required Dynamic Inputs

- `board_id` and `cycle_version` are required to derive canonical `BOARD_ROOT`.
- `spec_id` is required when the selected mode targets one spec package.
- `candidate_id` is required only when a discovery candidate document path is needed.
- If explicit `BOARD_ROOT` conflicts with supplied dynamic ids or repository truth, stop instead of guessing.
