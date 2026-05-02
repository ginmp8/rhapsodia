# Developer Artifact Standards

Load when MAGIA creates, updates, validates, or decides whether to create execution-grounded technical documentation.

## Ownership

Mago documents intended design. Magia documents implementation reality. MAGIA artifacts must be grounded in code, tests, command output, runtime evidence, dependency behavior, or selected Mago package evidence. They must not rewrite PRD, acceptance criteria, roadmap priority, stakeholder commitments, or product intent.

## Canonical Artifact Set

- implementation-notes.md: non-trivial implementation or plan divergence; actual code flow; canonical execution log for RALPH task history. Template: `assets/templates/implementation-notes.md.template`.
- complexity-reduction-evidence.md: behavior-preserving simplification/de-abstraction/refactor; before/after, removed/retained abstractions, validation, rollback. Template: `assets/templates/complexity-reduction-evidence.md.template`.
- implementation-adr.md or implementation-adrs/<adr_id>.md: material implementation decision with future maintenance impact. Template: `assets/templates/implementation-adr.md.template`.
- validation-evidence.md: code/docs/state changed or validation requested; executed, failed, skipped, static checks; canonical validation evidence for RALPH execution. Template: `assets/templates/validation-evidence.md.template`.
- runbook.md: operational behavior, reprocessing, mitigation, rollback. Template: `assets/templates/runbook.md.template`.
- migration-execution-note.md: schema/data/topic/cache/index/file migration prepared or executed; actual path and rollback. Template: `assets/templates/migration-execution-note.md.template`.
- contract-change-note.md: API/event/schema/interface/file contract change; compatibility and consumer impact. Template: `assets/templates/contract-change-note.md.template`.
- observability-note.md: logs, metrics, traces, dashboards, alerts, correlation changes. Template: `assets/templates/observability-note.md.template`.
- troubleshooting.md: symptoms/support procedures; diagnosis and corrective actions. Template: `assets/templates/troubleshooting.md.template`.
- security-risk-note.md: security, permissions, PII, secrets, auth, encryption, compliance. Template: `assets/templates/security-risk-note.md.template`.
- technical-gap-note.md: Mago spec incomplete, wrong, ambiguous, or contradicted; gap, safe local decision, handoff. Template: `assets/templates/technical-gap-note.md.template`.

## Path Rules

Prefer existing repository docs conventions. If none and RALPH executes a selected spec, place artifacts under:

```text
BOARD_ROOT/specs/<spec_id>/
```

Use subdirectories only for multi-entry families:

```text
BOARD_ROOT/specs/<spec_id>/implementation-adrs/<adr_id>.md
```

For ADHOC without a board package, use existing docs convention; if none, report the proposed path before writing unless documentation creation was explicitly allowed.

## Quality Bar

Every MAGIA technical artifact includes scope/task/spec link when available, evidence inspected, actual decision or implementation fact, validation status with skipped checks and reasons, residual risks/unknowns, and handoff decision `none`, `mago`, `magnomo`, or `both`.



Terminology: use code/runtime evidence for implementation facts, operators/devs for runbook audience, Schema/data/topic/cache/index/file for migration scope, and implementation-adrs/<adr_id>.md for multi-ADR paths.

## Creation Rules

Create docs when they materially help future implementation, maintenance, validation, operation, security, or handoff. Do not create formal docs for trivial style, naming, or self-evident tiny changes. Prefer one focused artifact; start with implementation-notes.md and add implementation-adr.md only for consequential decisions.

## ADR Criteria

Create an execution-grounded ADR when a decision affects architecture, public contracts, persistence, distributed consistency, retries, idempotency, ordering, concurrency, security, migration, rollback, operability, observability, future extension, a Mago planned approach or execution-handoff plan that could not be implemented as written, or dependency/runtime trade-offs. Do not create ADRs for routine library use, small refactors, formatting, naming, or local style.

## Handoff Rules

- Mago: missing/changed technical intent, architecture, public contract, task structure, validation plan, security posture, or data model beyond selected task.
- Magnomo: delivery risk, deadline change, stakeholder communication, release-note need, owner change, or accepted business risk.
- Do not silently update the wrong skill's artifacts.

## Complexity-Reduction Evidence

Create complexity-reduction-evidence.md when Magia removes, merges, inlines, or simplifies abstractions; reduces layers/indirection; changes module boundaries; replaces speculative configurability with explicit behavior; or executes a Mago complexity-reduction plan. Prove preserved behavior through executed checks, static reasoning, or labeled not-run gaps. Skip for formatting-only edits, trivial renames, or changes without maintainability-relevant structure.
