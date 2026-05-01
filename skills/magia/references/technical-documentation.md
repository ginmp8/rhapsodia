# Technical Documentation and Implementation ADRs

Load this reference when MAGIA creates or updates developer documentation, implementation decisions, or execution-grounded Architecture Decision Records. For the full artifact taxonomy, load [developer-artifact-standards.md](developer-artifact-standards.md).

## Ownership

MAGIA owns technical documentation directly tied to implementation, validation, or operation:

- implementation notes;
- implementation decisions discovered during execution;
- implementation ADRs grounded in repository, test, command, or runtime evidence;
- validation evidence;
- migration and rollback notes;
- contract change notes;
- observability notes;
- runbooks and troubleshooting guides;
- security and risk notes;
- technical gap notes for Mago handoff.

MAGIA must not refine PRDs, redefine acceptance criteria, resequence roadmap work, create stakeholder status, or record delivery governance decisions.

## Canonical Paths

Prefer existing repository conventions when present. If no convention exists and RALPH is executing a spec, use spec-local paths:

```text
BOARD_ROOT/specs/<spec_id>/implementation-notes.md
BOARD_ROOT/specs/<spec_id>/validation-evidence.md
BOARD_ROOT/specs/<spec_id>/runbook.md
BOARD_ROOT/specs/<spec_id>/technical-gap-note.md
BOARD_ROOT/specs/<spec_id>/implementation-adrs/<adr_id>.md
```

For ADHOC work without a board package, use the repository's existing docs convention. If none exists, report the proposed path before writing unless the user explicitly allowed documentation creation.

## ADR Creation Criteria

Create or update an implementation ADR only when the decision is material for future maintainers and one or more are true:

- Mago did not specify the implementation approach and repository evidence forced a choice;
- tests or runtime behavior disproved the expected approach;
- a dependency limitation required a different implementation;
- a concurrency, idempotency, retry, ordering, data integrity, security, migration, rollback, observability, or operability trade-off was made;
- the decision affects future debugging, operability, or extension.

Do not create an ADR for trivial local code style, naming, small refactors, or straightforward implementation details that are already obvious from the code.

## Required ADR Content

An implementation ADR must include:

- `Status`: proposed, accepted, superseded, deprecated, or rejected.
- `Context`: code/runtime facts that forced the decision.
- `Decision`: the implementation choice.
- `Alternatives Considered`: options evaluated and why rejected.
- `Consequences`: trade-offs, risks, operational impact, and future constraints.
- `Evidence`: files inspected, commands run, tests, logs, or Mago artifacts.
- `Validation`: executed checks and remaining gaps.
- `Scope Guard`: why the decision stays within task/product intent.
- `Handoff`: `none` or the specific Mago/Magnomo handoff required.

## Validation Rules

- Separate executed validation from planned validation.
- Cite command names and pass/fail/not-run status.
- If validation cannot run, state why and provide the strongest truthful fallback evidence.
- Do not claim production readiness, deployment, PR creation, or stakeholder acceptance unless current evidence proves it.

