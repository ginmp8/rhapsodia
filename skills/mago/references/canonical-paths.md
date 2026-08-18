# Canonical Paths

This file is the single source of truth for board-root and package-path resolution.

## Canonical Defaults

```text
CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<year>/cycles/<cycle_id>/
CANONICAL_SPEC_PACKAGE = {BOARD_ROOT}specs/<spec_id>/
CANONICAL_SPEC_REGISTRY = {BOARD_ROOT}registry/<spec_id>.yaml
```

A canonical root contains `cycle.yaml`. `cycle_id` is immutable and includes a creation date and readable cycle key:

```text
cycle-<yyyy-mm-dd>-<cycle-key>
```

A spec identity is:

```text
spec-<yyyy-mm-dd>-<feature-key>
```

Canonical examples are `cycle-2026-04-20-q2-delivery` and `spec-2026-04-20-csv-export-filtered-columns`. Do not append a ULID, hash, UUID, counter, sequence, or any other generated suffix.

The `<year>` segment must match the creation year encoded in `cycle_id` and `cycle.yaml.created_at`.

## Operational Resolution

- `BOARD_ROOT` is the active write boundary.
- Prefer an explicit `BOARD_ROOT` after validating it against repository truth.
- Otherwise derive it from concrete `board_id`, `year`, and `cycle_id`.
- Derive package work from `BOARD_ROOT/specs/<spec_id>/`.
- Derive registry work from `BOARD_ROOT/registry/<spec_id>.yaml`.
- Never create aliases, duplicate trees, or a second source of truth.
- Old directory layouts are read-only source material for `adapt`; they are never resolved as an active `BOARD_ROOT`.

## Required Dynamic Inputs

- `board_id`;
- `year` or a year inferable from `cycle_id`;
- `cycle_id`;
- `spec_id` for spec/package work.

If an explicit root conflicts with supplied IDs, metadata, or repository truth, stop instead of guessing.
