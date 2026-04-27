# Technical Design Mode

Use for `technical-design`.

`technical-design` creates or refines technical-design.md for one selected spec when the work needs explicit architecture alignment before implementation.

## Rules

- `BOARD_ROOT` and `spec_id` are required.
- Keep technical-design.md under `BOARD_ROOT/specs/<spec_id>/`.
- Use scripts/write_artifact_scaffold.py <BOARD_ROOT>/specs/<spec_id>/technical-design.md when creating the file.
- Open [../artifacts/technical-design.md](references/artifacts/technical-design.md) before writing or validating content.
- Load only the selected package, relevant discovery or roadmap evidence, and directly relevant repository code or tests.
- Keep product requirements in prd.md; keep executable decomposition in tasks.md; keep validation expectations in validation.md; keep evolving assumptions and decisions in notes.md.
- Do not implement code, write repository execution steps, or claim validation evidence.
- Validate with scripts/validate_artifact.py <BOARD_ROOT>/specs/<spec_id>/technical-design.md.

## Design Depth

Create or expand technical-design.md only when the selected spec has material architecture or contract risk: new system boundaries, external integrations, public APIs, persistence or migration shape, identity/access boundaries, sensitive data, production rollout, observability, rollback, or meaningful alternatives. If the work is a straightforward product or task clarification, keep design inline in prd.md, tasks.md, validation.md, or notes.md instead of creating a separate design artifact.

Use `project_size` to size the artifact:

- `small`: brief context, solution, risks, testing, and open questions; optional sections may be `unknown` when evidence is thin.
- `medium`: include component responsibilities, data flow, contracts, key alternatives, dependencies, failure modes, and rollout concerns when supported.
- `large`: include explicit decision criteria, rejected alternatives, migration or phased rollout shape, observability, rollback triggers, and security posture for every material boundary.
- `unknown`: start small and record the sizing uncertainty in `Open Questions`.

Use `project_types` to decide which sections need real content through product-agnostic risk tags. `identity_access`, `sensitive_data`, `regulated_data`, `secret_handling`, and `trust_boundary` require security coverage. `production_change`, `infrastructure_change`, `external_integration`, `migration`, `data_change`, and `public_contract` require testing, monitoring, rollback, and failure-mode coverage. Missing facts should remain explicit unknowns or open questions, not invented design.

## Knowledge Verification Chain

Before making a technical decision, verify in this order:

1. selected spec package and linked MAGO/Magnomo evidence
2. repository code, tests, configs, schemas, and existing patterns
3. repository docs and local planning notes
4. official vendor or framework documentation when an external dependency or API is involved
5. explicit uncertainty in `Open Questions`

Do not present guessed APIs, framework behavior, operational guarantees, or compliance properties as facts. If a decision depends on unavailable information, write the design around the known boundary and record what must be verified.

## Content Focus

- Context, problem, scope, and future considerations.
- Technical solution at component, contract, data-flow, dependency, and failure-mode level.
- Architecture decisions with rejected alternatives and accepted trade-offs when material.
- Security, monitoring, observability, rollback, and testing strategy when the work touches production, auth, payment, PII, external integrations, or migrations.
- High-level implementation plan only. Detailed `taskNNN` work belongs in tasks.md.

## Quality Bar

- The design should survive implementation framework changes.
- Every contract or decision should be traceable to repository truth, discovery evidence, roadmap evidence, or explicit user input.
- Missing facts stay `unknown`, empty lists, or explicit open questions.
- Diagrams should clarify architecture or sequence, not decorate the document.
