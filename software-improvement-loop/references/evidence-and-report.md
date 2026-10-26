# Evidence and report

## Record once per experiment

- Goal, primary mode, authorized paths, constraints and exclusions.
- Source baseline identity (commit and/or verifiable working tree snapshot) and candidate identity; experiment and evaluator/harness version or hash when appropriate.
- Frozen target and guardrails; relevant test/benchmark commands, environment, fixtures and expected failure signatures.
- Hypothesis and actual changed paths, test changes, iteration attempts and stop/budget consumption.
- Execution observations: exact commands, exit codes, test totals and failures, measurement samples, environment comparability and any flakiness.
- Check whether existing user changes and protected artifacts were untouched; identify incomplete rollback.
- Decisions: `keep`, `revert`, `inconclusive`, `blocked` with direct evidence and residual risk.

## Result distinctions

- `measured`: an actual benchmark/test was executed; provide conditions and raw evidence or linked artifact.
- `verified`: a specific claim passed a suitable executable oracle; name its limits.
- `observed`: a specific artifact/diff/trace was read but not independently proven.
- `inferred`: reasonable explanation not confirmed by a test; do not equate with measured.
- `planned` or `not-run`: workflow/test described but not executed.

A passing metric report only supports a bounded **numerical** comparison, not a final accepted software change. A successful feature test does not imply a performance gain. An LLM-written review is not a replacement for runtime evidence. If the worktree has unrelated modifications, record the limitation and do not imply an isolated candidate.

## User-facing summary

Use `assets/run-report.template.md` for a persisted report when useful. Otherwise a concise response should name the decision, before/after results, executed tests, changed files, important limitations, and recovery/merge state. Write in the user's language. Never report a merged or deployed state unless that action actually occurred and was authorized.
