# Developer Artifact Standards

Load this reference when MAGIA creates, updates, validates, or decides whether to create execution-grounded technical documentation.

## Ownership Model

Mago documents intended design. Magia documents implementation reality.

MAGIA artifacts must be grounded in code, tests, command output, runtime evidence, dependency behavior, or selected Mago package evidence. They must not rewrite PRD, acceptance criteria, roadmap priority, stakeholder commitments, or product intent.

## Canonical Artifact Set

| Artifact | Trigger | Purpose | Template |
|---|---|---|---|
| `implementation-notes.md` | Any non-trivial implementation or divergence from plan | Describe what changed in code and how the actual flow works | [assets/templates/implementation-notes.md.template](../assets/templates/implementation-notes.md.template) |
| `complexity-reduction-evidence.md` | Behavior-preserving simplification, de-abstraction, or refactor changed code structure | Capture before/after complexity, removed/retained abstractions, validation, rollback, and residual complexity | [assets/templates/complexity-reduction-evidence.md.template](../assets/templates/complexity-reduction-evidence.md.template) |
| `implementation-adr.md` or `implementation-adrs/<adr_id>.md` | Material implementation decision with future maintenance impact | Record execution-grounded architecture decision | [assets/templates/implementation-adr.md.template](../assets/templates/implementation-adr.md.template) |
| `validation-evidence.md` | Code/docs/state changed or validation requested | Record executed, failed, skipped, and static checks | [assets/templates/validation-evidence.md.template](../assets/templates/validation-evidence.md.template) |
| `runbook.md` | Feature has operational behavior, reprocessing, mitigation, or rollback needs | Give operators/devs a usable operating guide | [assets/templates/runbook.md.template](../assets/templates/runbook.md.template) |
| `migration-execution-note.md` | Schema/data/topic/cache/index/file migration was executed or prepared | Capture actual migration path and rollback facts | [assets/templates/migration-execution-note.md.template](../assets/templates/migration-execution-note.md.template) |
| `contract-change-note.md` | API/event/schema/interface/file contract changed | Capture compatibility and consumer impact | [assets/templates/contract-change-note.md.template](../assets/templates/contract-change-note.md.template) |
| `observability-note.md` | Logs, metrics, traces, dashboards, alerts, or correlation changed | Capture production signals and gaps | [assets/templates/observability-note.md.template](../assets/templates/observability-note.md.template) |
| `troubleshooting.md` | Known symptoms or support procedures exist | Capture diagnosis and corrective actions | [assets/templates/troubleshooting.md.template](../assets/templates/troubleshooting.md.template) |
| `security-risk-note.md` | Security, permissions, PII, secrets, auth, encryption, or compliance changed | Capture risk and mitigation evidence | [assets/templates/security-risk-note.md.template](../assets/templates/security-risk-note.md.template) |
| `technical-gap-note.md` | Mago spec is incomplete, wrong, ambiguous, or contradicted by code/runtime | Capture gap, safe local decision, and handoff | [assets/templates/technical-gap-note.md.template](../assets/templates/technical-gap-note.md.template) |

## Path Rules

Prefer existing repository documentation conventions when they exist. If none exist and RALPH is executing a selected spec, place execution-grounded artifacts under:

```text
BOARD_ROOT/specs/<spec_id>/
```

Use subdirectories only when the artifact family can have many entries:

```text
BOARD_ROOT/specs/<spec_id>/implementation-adrs/<adr_id>.md
```

For ADHOC work without a board package, use the repository's existing docs convention. If no convention exists, report the proposed path before writing unless the user explicitly allowed documentation creation.

## Required Quality Bar

Every MAGIA technical artifact must include:

- scope and task/spec link when available;
- evidence inspected;
- actual decision or implementation fact;
- validation status, including skipped checks and reasons;
- residual risks and unknowns;
- handoff decision: `none`, `mago`, `magnomo`, or `both`.

## Creation Rules

Create documentation when it materially helps future implementation, maintenance, validation, operation, security, or handoff. Do not create a formal document for trivial code style, obvious local naming, or details already self-evident from a tiny change.

Prefer one focused artifact over a large mixed document. When in doubt, start with `implementation-notes.md` and add a formal `implementation-adr.md` only for decisions with future consequence.

## ADR Criteria

Create an execution-grounded ADR when a decision affects one or more of:

- architecture, public contracts, persistence, distributed consistency, retries, idempotency, ordering, concurrency, security, migration, rollback, operability, observability, or future extension;
- a planned Mago approach that could not be implemented as written;
- a dependency or runtime limitation that forced a trade-off.

Do not create an ADR for routine library usage, small refactors, formatting, naming, or local code style.

## Handoff Rules

- Handoff to Mago when the artifact exposes missing or changed technical intent, architecture, public contract, task structure, validation plan, security posture, or data model beyond the selected task.
- Handoff to Magnomo when the artifact exposes delivery risk, deadline change, stakeholder communication, release-note requirement, owner change, or accepted business risk.
- Do not silently update the wrong skill's artifacts.



## Complexity-Reduction Evidence Criteria

Create `complexity-reduction-evidence.md` when Magia removes, merges, inlines, or simplifies abstractions; reduces layers or indirection; changes module boundaries; replaces speculative configurability with explicit behavior; or executes a Mago complexity-reduction plan. The artifact must prove preserved behavior through executed checks, static reasoning, or clearly labeled not-run validation gaps.

Do not create this artifact for formatting-only edits, trivial rename-only refactors, or changes that did not alter maintainability-relevant structure.
