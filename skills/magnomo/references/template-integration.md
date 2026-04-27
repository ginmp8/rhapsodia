# Template Integration

Use this reference when deciding which reusable template backs a Magnomo-owned artifact family. Templates are operational assets: scaffold or update them through bundled scripts, then validate the touched artifact.

## Delivery Templates

- `assets/templates/ops.yaml.template`: spec-scoped delivery metadata and operational state.
- `assets/templates/status.md.template`: spec-scoped stakeholder-readable delivery status.
- `assets/templates/stakeholder-brief.md.template`: spec-scoped stakeholder brief for alignment, timing, and risk communication.
- `assets/templates/replanning.md.template`: spec-scoped append-only replanning history.

## Portfolio and Roadmap Templates

- `assets/templates/portfolio.yaml.template`: board-scoped structured portfolio state.
- `assets/templates/portfolio.md.template`: board-scoped human-readable portfolio summary.
- `assets/templates/roadmap.yaml.template`: board-scoped structured roadmap.
- `assets/templates/roadmap.md.template`: board-scoped human-readable roadmap.
- `assets/templates/feature-map.yaml.template`: board-scoped roadmap-to-spec handoff map.

## Proposal and Decision Templates

- `assets/templates/rfc-proposals.md.template`: board-scoped RFC proposal log.
- `assets/templates/adr-records.md.template`: board-scoped ADR record log.

## Reporting Templates

- `assets/templates/feature-report.md.template`: spec-scoped feature report after delivery evidence is supplied.
- `assets/templates/release-notes.md.template`: board-scoped stakeholder-facing release notes.
- `assets/templates/internal-notes.md.template`: board-scoped internal delivery notes.

## Usage Rules

1. Prefer `scripts/write_artifact_scaffold.py` or `scripts/write_ops_scaffold.py` over manual structure creation when a template-backed artifact does not exist.
2. Prefer `scripts/update_template_lists.py` for supported mechanical list updates.
3. Preserve unknown facts as unknown in generated artifacts rather than filling template slots with inferred owners, dates, deployment status, review status, or validation facts.
4. Run the artifact validator and, for repository-facing writes, board-path validation after using a template.
