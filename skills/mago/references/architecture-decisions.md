# Architecture Decisions

Use when MAGO records planned architecture decisions, planned technical decisions, or Architecture Decision Records for one selected spec package.

## Ownership

MAGO owns architecture decisions that are made during planning or spec refinement. These include system boundaries, APIs, data contracts, persistence shape, eventing, workflow orchestration, security posture, observability design, migration approach, rollback strategy, dependency choice, and planned execution strategy before implementation begins.

Do not send architecture ADRs to nomia. nomia may record governance decisions that depend on technical evidence, but the architecture decision itself stays in MAGO or MAGIA.

MAGIA may create implementation ADRs when a decision is discovered during execution and grounded in code/runtime evidence. If that implementation ADR changes product intent, acceptance criteria, public contract, or the planned architecture materially, MAGIA must hand off to MAGO for planning alignment.

## Canonical Paths

Preferred spec-scoped planning decision log:

```text
BOARD_ROOT/specs/<spec_id>/architecture-decisions.md
```

Optional per-decision ADR files may be used when the repository or board package already has that convention:

```text
BOARD_ROOT/specs/<spec_id>/adrs/<adr_id>.md
```

Repository-wide ADRs may be created only when the user explicitly selects a repository ADR convention and the write scope allows it. Otherwise keep decisions spec-scoped.

Do not create architecture ADRs under nomia governance decision logs.

## Required ADR Content

An architecture decision must include:

- `Status`: proposed, accepted, superseded, deprecated, or rejected.
- `Context`: technical forces and constraints.
- `Decision`: the selected technical direction.
- `Alternatives Considered`: options evaluated and why they were not chosen.
- `Consequences`: trade-offs, risks, operational impact, migration impact, and future constraints.
- `Evidence`: repository files, existing docs, nomia handoff, external dependency docs, or explicit user input.
- `Validation Expectations`: checks Magia should run or evidence needed during execution.
- `Owner`: person, group, role, or `unknown`.
- `Links`: PRD, technical design, tasks, validation plan, tickets, or `none`.

## Quality Rules

- Keep product intent in prd.md; keep planned architecture and planned technical choices in technical-design.md or ADRs.
- Record unknowns explicitly instead of inventing facts.
- Prefer one clear decision per ADR.
- Include rejected alternatives when they influenced the chosen direction.
- Include accepted downside or trade-off.
- Distinguish planned validation from executed validation.
- If a decision is purely local and can be captured as a task note, do not overproduce a formal ADR.
- If the decision affects public contracts, data persistence, security posture, concurrency, distributed consistency, regulated data, production rollback, or observability, prefer a formal ADR.

## Handoff to Magia

When an ADR affects execution, add enough information for Magia to implement without guessing:

- changed modules or expected code areas when known;
- constraints and non-goals;
- validation commands or checks when known;
- migration and rollback expectations;
- contract compatibility requirements;
- observability and operational requirements;
- risks that must be revalidated during implementation.

