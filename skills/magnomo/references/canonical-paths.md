# Canonical Paths

Use this file as the single source of truth for canonical path definitions and override resolution.

## Canonical Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<cycle_version>/`
- linked spec packages, when needed, always live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`

## Operational Resolution

- `BOARD_ROOT` is the active board root for repository-facing Magnomo artifacts.
- If the prompt provides `BOARD_ROOT`, use it after validating that it matches repository truth.
- Otherwise derive `BOARD_ROOT` from `CANONICAL_BOARD_ROOT` with concrete `board_id` and `cycle_version`.
- Board-scoped Magnomo artifacts derive from `BOARD_ROOT`.
- Spec-scoped Magnomo artifacts derive from `BOARD_ROOT/specs/<spec_id>/`.
- Do not invent alternate governance roots or ad hoc nested output roots.

## Required Dynamic Inputs

- `board_id` and `cycle_version` are required to derive canonical `BOARD_ROOT`.
- `spec_id` is required whenever a mode writes a spec-scoped Magnomo artifact.
- If explicit `BOARD_ROOT` conflicts with supplied dynamic ids or repository truth, stop instead of guessing.
