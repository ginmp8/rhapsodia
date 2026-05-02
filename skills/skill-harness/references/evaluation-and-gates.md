# Evaluation and Gates

Use for measurable target-skill acceptance criteria.

## Static Score

Useful 0-100 dimensions: trigger specificity; inputs/assumptions; workflow/modes; output contract; supporting resources; validation/gates; scenario readiness; maintainability; safety/blocked paths/evidence discipline; packaging readiness. Scores guide; required gates override.

## Required Gates

A target is not ready if any required gate fails: exactly one `SKILL.md`; frontmatter `name` and `description`; specific description with negative boundary; clear inputs/outputs; scope boundaries and stops; no unresolved scaffold placeholders; referenced resources and workflow-mentioned `assets/templates/` paths exist; operational assets integrated by workflow/copy/fill/script/validator; intended scripts have commands; validation criteria exist; dynamic facts are not permanent truth; blocked paths and secrets are protected.

## Supporting Resources

Classify warnings before deleting. An asset is integrated if referenced from `SKILL.md` or loaded references, copied/filled by workflow, rendered/updated/checked by script, or covered by structural/package validation. Delete/migrate only evidence-backed unused scaffolding, duplicates, obsolete/misleading/oversized assets, or explanatory prose better placed in `references/`.

## Behavioral Metrics

Use only for supplied/executed prompts/results. Activation precision = correct activations / actual activations. Activation recall = correct activations / expected activations. Output conformance = conforming outputs / executed prompts. Criteria coverage = satisfied / expected criteria. Robustness = passed / executed edge cases. Rework rate = manually corrected / executed prompts. If not measured, label `not measured` and propose a suite.

## Saturated Metrics and Decisions

If a benchmark is 100/100, keep it as a gate and add a non-saturated auxiliary metric before claiming improvement: scenario conformance, strict checklist coverage, package pass/fail plus new gate count, reduced risks, or evidence completeness. Do not claim improvement from an unchanged saturated score.

Severity: `blocker`, `major`, `minor`, `informational`. Decisions: `accept`, `accept with risks`, `reject`, `plan only`, `needs context`.
