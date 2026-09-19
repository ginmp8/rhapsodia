# ADHOC Mode

## Canonical Rules

- `BOARD_ROOT` is optional unless durable MAGIA docs are touched.
- If prompt provides `BOARD_ROOT`, use it after validation.
- If durable docs are required and no override exists, derive the package path from `BOARD_ROOT` via `references/canonical-paths.md`.
- Code-only runs with no durable MAGIA docs need no board path.

## Use When

Use ADHOC for direct repository work not driven by active the selected registry entry plus spec package: direct fixes, small implementation tasks without a planning package, targeted validation, or hardening outside RALPH.

## Workflow

1. Read request.
2. Load minimum relevant code/docs.
3. Inspect impacted files.
4. Make the smallest safe change.
5. Run validation proving the change.
6. Summarize changes, validation, and remaining risks.

## Rules

Do not auto-load board artifacts unless the task depends on them. Keep scope local. Update durable MAGIA planning/execution/validation/architecture docs only under `BOARD_ROOT`. Do not create ad hoc MAGIA docs elsewhere to compensate for missing board/version context. Do not claim broader completion than evidence proves.
