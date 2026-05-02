# Technical Design Artifact

## technical-design.md

Optional spec-scoped MAGO planning artifact. Use it when a selected spec needs explicit architecture alignment before execution: new system boundaries, integrations, migrations, persistence shape, public contracts, security posture, observability, rollback, planned execution strategy, meaningful alternatives, or decisions that may require ADRs.

technical-design.md belongs under:

```text
BOARD_ROOT/specs/<spec_id>/technical-design.md
```

It supports prd.md, tasks.md, validation.md, notes.md, and architecture decision records; it does not replace them. Keep product intent in prd.md, detailed executable decomposition in tasks.md, intended validation in validation.md, evolving rationale in notes.md, and durable architecture decisions in architecture-decisions.md or adrs/<adr_id>.md when the decision deserves a formal ADR.

## Required Structure

Preserve these headings:

- `# Technical Design - <title>`
- `## Context`
- `## Problem Statement`
- `## Scope`
- `## Technical Solution`
- `## Architecture Decisions`
- `## Security Considerations`
- `## Testing Strategy`
- `## Monitoring and Observability`
- `## Rollback Plan`
- `## Risks`
- `## Execution Handoff Plan`
- `## Open Questions`

Preserve YAML front matter fields from the template. `project_size` uses `small`, `medium`, `large`, or `unknown`. `project_types` is a product-agnostic risk-tag list, such as `feature`, `external_integration`, `migration`, `infrastructure_change`, `identity_access`, `sensitive_data`, `regulated_data`, `data_change`, `public_contract`, or `production_change`.

## Writing Rules

- Generate prose in the same language as the user request or surrounding package when that language is already established; keep YAML keys, ids, filenames, and enum-like values in canonical English.
- Focus on architecture decisions, planned execution strategy, and contracts, not implementation code.
- Include API contracts, data schemas, component responsibilities, sequence or architecture diagrams, dependency assumptions, rollback strategy, and ADR candidates when they materially affect execution.
- Do not include CLI command recipes, framework-specific decorators, class bodies, migration command lines, deployment runbooks, or claimed execution evidence.
- If identity/access, sensitive-data, regulated-data, trust-boundary, or production-change risk is in scope, treat `Security Considerations`, `Monitoring and Observability`, and `Rollback Plan` as required content, not optional prose.
- For small work, keep the document short and use unknowns honestly. For medium or large work, include alternatives, decision criteria, contract details, failure modes, and rollout concerns when evidence supports them.

## ADR Trigger Rules

Create or update an architecture decision record when a decision affects one or more of:

- public API or event/data contract;
- persistence model, migration strategy, or retention behavior;
- distributed consistency, idempotency, retries, ordering, or concurrency;
- security, privacy, compliance, regulated data, or trust boundary;
- workflow orchestration, messaging, integration boundary, or dependency choice;
- observability, operational recovery, rollback, or production support model;
- meaningful trade-off that future implementers must understand.

Use `references/architecture-decisions.md` and `references/adr-quality.md` for ADR content and quality. Do not create architecture ADRs in Magiarca.

## Evidence and Optional Sections

Design facts must be traceable to the selected package, repository truth, local docs, supplied Magiarca handoff evidence, or official dependency documentation. When the chain does not establish a fact, use `unknown` prose and add an `Open Questions` item.

The canonical top-level headings are fixed, but useful subsections may be added when supported by evidence. Diagrams should clarify architecture or sequence, not decorate the document.
