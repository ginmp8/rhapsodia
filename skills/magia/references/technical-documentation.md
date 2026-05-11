# Technical Documentation and Implementation ADRs

Load when creating/updating developer docs, implementation decisions, or execution-grounded ADRs. For taxonomy, load `references/developer-artifact-standards.md`.

## Ownership

MAGIA owns implementation-linked docs: implementation notes, execution decisions, ADRs grounded in repository/test/command/runtime evidence, validation evidence, migration/rollback notes, contract notes, observability notes, runbooks, troubleshooting, security/risk notes, and technical gap notes for Mago handoff.

MAGIA must not refine PRDs, redefine acceptance criteria, resequence roadmap work, create stakeholder status, or record delivery governance decisions.

## Canonical Paths

Prefer existing repo docs conventions. If none and RALPH executes a spec, use spec-local paths:

```text
BOARD_ROOT/specs/<spec_id>/implementation-notes.md
BOARD_ROOT/specs/<spec_id>/validation-evidence.md
BOARD_ROOT/specs/<spec_id>/runbook.md
BOARD_ROOT/specs/<spec_id>/technical-gap-note.md
BOARD_ROOT/specs/<spec_id>/implementation-adrs/<adr_id>.md
```

For ADHOC without a board package, use existing docs convention; if none, report the proposed path before writing unless docs creation was explicitly allowed.

## ADR Creation

Create/update an implementation ADR only when future maintainers need it for code/runtime or task/product consequences and one or more hold: Mago omitted the approach or execution-handoff plan and repo evidence forced a choice; tests/runtime disproved the planned approach; dependency limits forced a different implementation; concurrency, idempotency, retry, ordering, data integrity, security, migration, rollback, observability, or operability trade-off occurred; the decision affects future debugging, operations, or extension.

Do not create ADRs for trivial style, naming, small refactors, or obvious local details.

## Required ADR Content

Include `Status`, `Context`, `Decision`, `Alternatives Considered`, `Consequences`, `Evidence`, `Validation`, `Scope Guard`, and `Handoff` (`none` or specific Mago/nomia handoff).

## Validation Rules

Separate executed from planned validation. Cite command names and pass/fail/not-run status. If validation cannot run, state why and provide the strongest truthful fallback. Do not claim production readiness, deployment, PR creation, or stakeholder acceptance without current evidence.
