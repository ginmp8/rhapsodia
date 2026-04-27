# ADHOC Mode

## Canonical Rules

- `BOARD_ROOT` is optional unless the run touches durable MAGIA documentation.
- If the prompt provides `BOARD_ROOT`, use it after validation.
- If durable MAGIA docs are required and no override is provided, derive the needed package path from `BOARD_ROOT` via `references/canonical-paths.md`.
- If the run is code-only and no durable MAGIA docs are in scope, no canonical board path needs to be resolved.

## When to Use ADHOC

Use ADHOC when the work is a direct repository change and execution is not driven by an active spec-catalog.yaml plus a selected spec package.

Typical cases:

- a direct user-requested fix
- a small implementation task without a current planning package
- a targeted validation or hardening pass outside the RALPH workflow

## ADHOC Workflow

1. Read the user request.
2. Load only the minimum relevant code and docs.
3. Inspect the impacted files.
4. Make the smallest safe change.
5. Run the validation needed to prove the change.
6. Summarize what changed, what was validated, and any remaining risks.

## ADHOC Rules

- Do not automatically load board artifacts unless the task clearly depends on them.
- Keep scope local to the requested change.
- Update durable MAGIA planning, execution, validation, or architecture docs only under `BOARD_ROOT`.
- Do not create ad hoc MAGIA documentation elsewhere to compensate for missing board or version context.
- Do not claim broader completion than the executed change actually proves.
