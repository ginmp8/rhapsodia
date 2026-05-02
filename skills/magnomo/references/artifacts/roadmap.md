# Roadmap Artifacts

Roadmap artifacts belong to Magnomo. Mago may consume them as upstream evidence, but they do not replace `spec-catalog.yaml`, `prd.md`, or Mago-owned planning artifacts.

## roadmap.yaml

Machine-readable roadmap source for initiatives, feature candidates, sequencing, dependencies, MVP boundaries, confidence, and candidate Mago spec readiness.

Required top-level keys: `schema_version`, `roadmap_id`, `title`, `owner`, `horizon`, `features`. Optional top-level keys: `description`, `goals`, `outcomes`, `themes`, `stakeholders`, `constraints`, `assumptions`, `success_measures`, `risks`.

Each feature includes `feature_key`, `name`, `problem`, `outcome`, `horizon`, `commitment`, `confidence`, `dependencies`, `ready_for_spec`, `candidate_spec_id`. Recommended fields: `scope_summary`, `mvp_boundary`, `later_phases`, `non_goals`, `stakeholders`, `risks`, `notes`, `source_links`.

Enums: `horizon` = `unknown`, `now`, `next`, `later`, `future`; `commitment` = `unknown`, `committed`, `targeted`, `exploratory`, `parking_lot`; `confidence` = `unknown`, `low`, `medium`, `high`.

Validation: `schema_version` is `1`; `feature_key` is unique lowercase hyphen-case; `dependencies` reference existing feature keys; `candidate_spec_id` is `null` or `specNNN`; `ready_for_spec: true` without `candidate_spec_id` warns; candidate spec values match the same feature in `feature-map.yaml` when present. Populate `goals`, `outcomes`, `themes`, `stakeholders`, `constraints`, `assumptions`, `success_measures`, `risks`, and `features` with `scripts/update_template_lists.py <roadmap.yaml> --data <payload.yaml>`; do not hand-shape list entries.

## roadmap.md

Human roadmap narrative.

Required sections: `# Roadmap`, `## Context`, `## Themes`, `## Goals And Outcomes`, `## MVP Boundary`, `## Sequencing`, `## Dependencies`, `## Risks`, `## Stakeholders`, `## Open Decisions`. Optional: `## Success Measures`, `## Non-Goals`, `## Later Phases`, `## Mago Handoff Candidates`.

Narrative aligns with `roadmap.yaml`. Features marked ready for spec should appear in `feature-map.yaml`. Material undecided roadmap proposals belong in `rfc-proposals.md`; accepted material roadmap changes belong in `governance-decisions.md`. Material changes include priority, sequencing, confidence, scope, dependency, MVP boundary, `ready_for_spec`, and `candidate_spec_id` changes. For RFC shape use [rfc.md](rfc.md); for governance-decision append-only rules use [governance-decision.md](governance-decision.md).

## feature-map.yaml

Machine-readable handoff map from Magnomo roadmap features to candidate Mago specs. Use only as upstream evidence for Mago, never as a generated task plan.

Required top-level keys: `schema_version`, `roadmap_id`, `features`. Each feature handoff includes `feature_key`, `ready_for_spec`, `candidate_spec_id`, `title`, `scope_summary`, `dependencies`, `recommended_mago_mode`. Recommended fields: `handoff_status`, `source_summary`, `mago_inputs`, `notes`.

Validation: every `feature_key` exists in `roadmap.yaml`; feature keys are unique; `candidate_spec_id` is `null` or `specNNN`; `ready_for_spec` and `candidate_spec_id` match the corresponding `roadmap.yaml` feature; dependencies reference existing roadmap feature keys; file must not contain implementation tasks, acceptance criteria, code instructions, or Magia execution evidence. Populate `features` with `scripts/update_template_lists.py <feature-map.yaml> --data <payload.yaml>`; do not hand-shape handoff list entries.
