# Canonical paths by storage profile

Default: `artifact-native`. Use `docs/product/<work_item_id>/` or an explicitly authorized owner root. See [native operation](artifact-native.md) for identity, publication and validation. No Board root, year, cycle or shared registry is required. Sidecars remain adjacent to their source files; derived views live outside all producer roots.

## Explicit legacy-board compatibility only

The following retained path contract applies only to an explicitly selected `legacy-board` maintenance/migration operation. Do not apply it to native work.

# Canonical Paths

Single source for nomia path defaults and runtime root resolution.

## Defaults

- `CANONICAL_BOARD_ROOT = docs/boards/<board_id>/<year>/cycles/<cycle_id>/`
- Linked spec packages live under `{CANONICAL_BOARD_ROOT}specs/<spec_id>/`.
- Existing Mago registry records live under `{CANONICAL_BOARD_ROOT}registry/<spec_id>.yaml`; nomia may read or link them but never create or modify them.

A canonical cycle identity is immutable and uses:

```text
cycle-YYYY-MM-DD-cycle-key
```

A canonical spec identity is immutable and uses:

```text
spec-YYYY-MM-DD-feature-key
```

The `<year>` directory must match the date year encoded in `cycle_id`. Canonical ids are supplied by the user, received through handoff, or evidenced by an existing repository artifact. A non-null candidate uses `candidate_spec_id_provenance`. nomia records provenance, must not mint planning identities, and does not create, choose, correct, rename, register, or replace ids.

## Resolution

- `BOARD_ROOT` is the active root for repository-facing nomia artifacts.
- Use prompt-provided `BOARD_ROOT` after validating repository truth; otherwise derive it from concrete `board_id`, `year`, and `cycle_id`.
- Infer `year` from `cycle_id` only when it is not supplied; reject conflicts.
- Board-scoped artifacts derive from `BOARD_ROOT`.
- Spec-scoped artifacts derive from `BOARD_ROOT/specs/<spec_id>/`.
- Do not invent alternate governance roots, aliases, missing packages, parallel docs roots, registry entries, or aggregate catalog files.
- Old layouts and ids ending in `--<ulid>` are read-only migration input for `governance-adapt`; they are never active write roots, are never converted automatically, and must not appear in canonical outputs.

## Dynamic Inputs

`board_id` and `cycle_id` are required to derive `BOARD_ROOT`; `year` may be supplied or inferred from the canonical `cycle_id`; `spec_id` is required for repository-facing spec-scoped writes. If explicit `BOARD_ROOT` conflicts with dynamic ids or repository truth, stop rather than guess.
