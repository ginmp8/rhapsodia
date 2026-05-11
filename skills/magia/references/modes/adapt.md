# ADAPT Mode

Use ADAPT only to convert legacy execution-record content into current MAGIA-owned artifacts before normal RALPH execution, validation, heal, or closure. ADAPT is not implementation, planning, governance, or release reporting.

## Scope

Inputs are legacy `notes.md` Execution Log sections and legacy command-result sections in `validation.md`. Outputs are current `implementation-notes.md` and `validation-evidence.md`. Treat the legacy files as one-time conversion inputs, not operational fallback evidence.

## Rules

- Create or update only MAGIA-owned execution artifacts: `implementation-notes.md` and `validation-evidence.md`.
- Do not rewrite PRD, tasks, acceptance criteria, planning notes, validation plan, roadmap, release notes, governance status, or stakeholder material.
- Do not mark tasks done, change manifest/spec-catalog status, or set `last_execution` unless current converted evidence is complete enough and the execution-state validators pass.
- Preserve uncertainty as `unknown`, `not-run`, residual risk, or blocker inside the current MAGIA-owned artifacts.
- After adaptation, run current validators against `implementation-notes.md` and `validation-evidence.md`; do not continue using legacy files as fallback.
- If conversion would require interpreting product intent, task definitions, architecture, or delivery status, stop and hand off to MAGO or nomia.

## Script

Use `scripts/adapt_legacy_execution_records.py <board_root> --spec-id <specNNN>` when available. The script performs best-effort extraction from legacy files and writes current MAGIA-owned artifacts without deleting MAGO-owned inputs.

## Output

Report files created/updated, legacy sections converted, unknowns, validation commands run, and any remaining gaps that block RALPH execution.
