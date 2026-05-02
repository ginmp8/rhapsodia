# Execution Evidence

Use when MAGIA produces structured downstream evidence, implementation notes, or execution-grounded technical documentation.

MAGIA evidence records implementation truth: repository changes, files touched, tests, commands, runtime output, blockers, implementation decisions, validation results, and residual risks. Magia does not create roadmap, release, status, stakeholder, portfolio, feature-reporting, governance RFC, or release-communication artifacts; downstream consumers interpret evidence themselves.

Use `implementation-notes.md` for execution history and implementation facts. Use `validation-evidence.md` for command results, failed/not-run checks, residual validation gaps, and blockers. Treat `notes.md` and `validation.md` as MAGO-owned planning inputs; legacy execution content in those files is ignored unless ADAPT mode is explicitly converting it into current MAGIA-owned artifacts.

For downstream consumption, label evidence provenance and closure state explicitly: `passed`, `failed`, `not-run`, `blocked`, `partial`, or `unknown`. Magnomo can summarize these labels in reports, but MAGIA must not write stakeholder-ready release language or governance approval.

## Evidence Types

Record only inspected, produced, or supplied evidence: files inspected/changed; commands; passed/failed tests; static reasoning; logs/runtime output with secrets redacted; implementation decisions/ADRs; blockers/follow-ups; validation gaps and not-run reasons.

## Decisions and ADR Links

For each technical decision or implementation ADR, include title, path, evidence source, validation status, scope guard proving product intent was not rewritten, and handoff target when Mago or Magnomo must review.

## Boundaries

MAGIA must not rewrite planning intent, PRD content, task definitions, roadmap inputs, product scope, acceptance criteria, feature sequencing, or delivery commitments. Planning-origin artifacts remain execution inputs; provenance is not a blocker. If planning content must change before safe implementation, record the concrete blocker/follow-up as execution evidence and hand off instead of editing planning artifacts. Do not create/update downstream governance or communication artifacts, or validators for them.
