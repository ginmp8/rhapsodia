# Canonical Paths

Single source for canonical path definitions and override resolution. This contract is carried locally by MAGIA; no other skill must be loaded, imported, or executed to resolve paths.

## Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<year>/cycles/<cycle_id>/`
- Spec packages live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`.
- The matching planning registry entry lives at `{CANONICAL_BOARD_ROOT}registry/<spec_id>.yaml`.

Canonical identities:

- `cycle_id = cycle-<yyyy-mm-dd>-<cycle-key>`
- `spec_id = spec-<yyyy-mm-dd>-<feature-key>`

The `<year>` path segment must match the creation year encoded in `cycle_id`.

## Resolution

- `BOARD_ROOT` is the active board root and the write boundary for durable MAGIA artifacts.
- If the prompt provides `BOARD_ROOT`, use it only after validating it against repository truth and `cycle.yaml`.
- Otherwise derive `BOARD_ROOT` from concrete `board_id`, `year`, and `cycle_id`.
- For spec-scoped work, derive the selected package from `BOARD_ROOT/specs/<spec_id>/`.
- Derive the registry entry from `BOARD_ROOT/registry/<spec_id>.yaml`.
- Treat catalog and queue files, when rendered externally, as generated inspection views rather than active board records or write targets.
- Treat old directory layouts and legacy ULID-bearing identifiers only as read-only ADAPT content; never resolve them as the active `BOARD_ROOT` or selected spec package.

## Required Inputs

- `board_id`, `year`, and `cycle_id`: required to derive `BOARD_ROOT`.
- `spec_id`: required for one selected spec package.
- If explicit `BOARD_ROOT` conflicts with dynamic ids, `cycle.yaml`, registry identity, manifest identity, or repository truth, stop instead of guessing.
