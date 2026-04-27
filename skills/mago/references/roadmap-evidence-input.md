# Roadmap Evidence Input

Mago may use provided roadmap evidence when defining or refining AI-ready planning specs. The evidence must come from the user, repository, or current run context. Mago owns only the resulting planning package.

This reference does not add roadmap, delivery, status, stakeholder, portfolio, feature-report, or release-note workflows to Mago.

## Boundary

Treat roadmap evidence as read-only input.

Mago may interpret roadmap and feature-map evidence, but must not create, update, normalize, validate, or own human-ready governance/reporting artifacts such as ops.yaml, status.md, stakeholder-brief.md, replanning.md, feature-report.md, release-notes.md, portfolio.md, or portfolio.yaml.

Mago must not depend on another skill package to interpret roadmap evidence. Do not import, execute, link to, or require external skill files or scripts.

## Roadmap Feature To Mago Spec

A roadmap feature can become a Mago spec when the evidence is specific enough to define or refine product scope.

Treat a feature map as a handoff index and a roadmap as structured source evidence.

Use `candidate_spec_id` only when it is provided, matches the active catalog sequence, and does not conflict with existing specs. Otherwise, follow normal Mago ordering and id assignment rules.

## Field Mapping

Apply these mappings conservatively:

- `feature_key`: use as Mago `feature_key` when stable and aligned with the capability. Never use it as `spec_id`.
- `candidate_spec_id`: use as `spec_id` only when it matches the active catalog sequence and does not conflict with existing specs.
- `title` or `name`: use as Mago `title`, adjusted only for clarity and consistency.
- `dependencies`: map to `depends_on_features`; map to `depends_on_specs` only when the referenced feature already has a known spec id.
- `business_outcome`, `outcome`, or `source_summary`: use as PRD problem, goal, impact, or success-context evidence. Do not turn it into delivery status.
- `mvp_boundary`: use to define PRD scope, non-goals, and acceptance boundaries.
- `risks`: record in notes.md, validation.md, or PRD risk sections as appropriate for the selected Mago mode.
- `open_questions`, unresolved roadmap RFC proposals, or unresolved ADR-linked roadmap changes: record as open questions or blockers. Do not resolve them without evidence.

If provided sources disagree, block or record uncertainty instead of silently choosing one.

## Do Not Copy Blindly

Do not copy roadmap values into unrelated Mago state.

Specifically:

- Do not copy `horizon`, `commitment`, `confidence`, or readiness into Mago `status`, `phase`, or execution state.
- Do not copy owner, stakeholder, target-date, release, status, or portfolio metadata into Mago planning artifacts.
- Do not turn roadmap narrative into acceptance criteria without converting it into testable product behavior.
- Do not turn MVP boundaries into tasks before product scope is coherent.
- Do not turn risks or open questions into requirements unless evidence resolves them.
- Do not use `candidate_spec_id` when it conflicts with the catalog or package layout.
- Do not add implementation guesses, delivery promises, or validation claims without repository truth or planning evidence.

## Traceability

Preserve a visible link from roadmap evidence to the Mago spec.

Use existing canonical traceability fields when the local schema supports them. If direct roadmap fields do not fit the schema, record linkage in notes.md or supporting discovery references.

Do not add new canonical manifest fields only for roadmap linkage.

Useful traceability details:

- roadmap paths from provided repository/user input
- `roadmap_id`
- `feature_key`
- `candidate_spec_id`
- source feature title
- unresolved roadmap RFC proposals, ADR records, or open questions

## Uncertainty

When roadmap evidence is incomplete or ambiguous:

- keep unknown values explicit
- record unresolved questions in notes.md or the touched planning artifact
- keep dependencies at feature level until a target spec id is known
- avoid assigning delivery status, owners, stakeholders, release timing, or validation evidence
- block define/refine handoff if the feature boundary is not specific enough for a truthful Mago spec

Mago remains planning-focused: it defines or refines AI-ready specs from evidence and leaves roadmap ownership and human-ready governance outside Mago.
