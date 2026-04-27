# Roadmap To Mago Contract

Magnomo produces roadmap artifacts that Mago may later consume as upstream human intent. This is a handoff contract, not a dependency on Mago files.

## Handoff Rules

- `feature_key` must be stable within a roadmap.
- `candidate_spec_id` should use `specNNN` only when a candidate id is known.
- `ready_for_spec: true` means the feature is ready for Mago to define or refine planning artifacts.
- `feature-map.yaml` handoffs should include `feature_key`, `candidate_spec_id`, `title`, `scope_summary`, `dependencies`, and `recommended_mago_mode`.
- `recommended_mago_mode` should describe the likely Mago planning action, such as `define`, `refine`, or `split`.
- The handoff may include product context, constraints, stakeholders, risks, outcomes, non-goals, MVP boundaries, acceptance themes, and whether a Mago `technical-design.md` is recommended before execution.
- The handoff must not include acceptance criteria, implementation-ready task decomposition, code execution steps, repository change instructions, validation plans, or Magia execution evidence.
- Candidate spec values must stay consistent between `roadmap.yaml` and `feature-map.yaml`.

## Roadmap-To-Specs Output Shape

When running `roadmap-to-specs`, produce or update `feature-map.yaml` entries with this shape:

```yaml
features:
  - feature_key: saved-query-sharing-controls
    ready_for_spec: true
    candidate_spec_id: spec014
    title: Saved-query sharing controls
    scope_summary: Admins need clearer saved-query visibility controls.
    dependencies: []
    recommended_mago_mode: define
    handoff_status: ready
    mago_inputs:
      - roadmap.yaml
      - roadmap.md
      - adr-records.md
    recommended_mago_artifacts:
      - technical-design.md
```
