# Technical Design Artifact

## technical-design.md

Optional spec-scoped MAGO planning artifact. Use it when a selected spec needs explicit architecture alignment before execution: new system boundaries, integrations, migrations, persistence shape, public contracts, security posture, observability, rollback, or meaningful alternatives.

technical-design.md belongs under:

```text
BOARD_ROOT/specs/<spec_id>/technical-design.md
```

It supports prd.md, tasks.md, validation.md, and notes.md; it does not replace them. Keep product intent in prd.md, detailed executable decomposition in tasks.md, intended validation in validation.md, and evolving rationale or repository findings in notes.md.

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
- `## Implementation Plan`
- `## Open Questions`

Preserve YAML front matter fields from the template. `project_size` uses `small`, `medium`, `large`, or `unknown`. `project_types` is a product-agnostic risk-tag list, such as `feature`, `external_integration`, `migration`, `infrastructure_change`, `identity_access`, `sensitive_data`, `regulated_data`, `data_change`, `public_contract`, or `production_change`.

## Writing Rules

- Generate prose in the same language as the user request or surrounding package when that language is already established; keep YAML keys, ids, filenames, and enum-like values in canonical English.
- Focus on architectural decisions and contracts, not implementation code.
- Include API contracts, data schemas, component responsibilities, sequence or architecture diagrams, dependency assumptions, and rollback strategy when they materially affect execution.
- Do not include CLI command recipes, framework-specific decorators, class bodies, migration command lines, deployment runbooks, or task checklists.
- If identity/access, sensitive-data, regulated-data, trust-boundary, or production-change risk is in scope, treat `Security Considerations`, `Monitoring and Observability`, and `Rollback Plan` as required content, not optional prose.
- For small work, keep the document short and use unknowns honestly. For medium or large work, include alternatives, decision criteria, contract details, failure modes, and rollout concerns when evidence supports them.

## Evidence and Optional Sections

Design facts must be traceable to the selected package, repository truth, local docs, supplied roadmap/governance evidence, or official dependency documentation. When the chain does not establish a fact, use `unknown` prose and add an `Open Questions` item.

The canonical top-level headings are fixed, but the following subsections may be added under them when useful:

- under `Scope`: `Success Metrics`, `Constraints`, or `Future Considerations`
- under `Technical Solution`: `Existing Reuse`, `External Dependencies`, `Failure Modes`, `Performance Requirements`, or `Migration Plan`
- under `Architecture Decisions`: `Alternatives Considered` or `Decision Criteria`
- under `Risks`: impact/probability/mitigation tables for material technical, operational, security, or delivery risks

Do not add these sections for ceremony. Add them only when they reduce implementation ambiguity or capture a material trade-off.

## Sizing and Risk Gates

Set `project_size` from the current evidence, not from effort optimism:

- `small`: single narrow boundary, low operational risk, no new public contract, no migration.
- `medium`: multiple touched boundaries, new contract, integration, persistence shape, or meaningful rollout/testing concern.
- `large`: multi-system change, data migration, production-risk rollout, trust-boundary or compliance impact, or several unresolved architectural alternatives.
- `unknown`: evidence is insufficient; the design must name what is unknown.

Use `project_types` as validator-visible risk signals. Include product-agnostic values such as `feature`, `external_integration`, `migration`, `infrastructure_change`, `identity_access`, `sensitive_data`, `regulated_data`, `secret_handling`, `trust_boundary`, `data_change`, `public_contract`, or `production_change` when they apply.

## Validation

Create with:

```bash
scripts/write_artifact_scaffold.py <BOARD_ROOT>/specs/<spec_id>/technical-design.md
```

Validate with:

```bash
scripts/validate_artifact.py <BOARD_ROOT>/specs/<spec_id>/technical-design.md
```

Use `scripts/validate_technical_design.py` directly only when debugging this artifact validator.
