# Skill Improvement Playbook

Use after the harness map identifies weaknesses.

## Improvement Areas

`SKILL.md`: fix weak activation, scope, inputs, modes, stops, outputs. Add/refine frontmatter triggers/exclusions, required inputs, mode selection, workflow, stops, output contracts, final checklist. Keep compact; move rubrics to references.

`references/`: add/split for conditional domain rules, rubrics, scenario schemas, source policies, troubleshooting, long examples. Every reference needs a `SKILL.md` loading condition.

`scripts/`: add when consistency beats model judgment: inventory/structure checks, schema validation, report generation, template rendering, deterministic transforms, package readiness. Require clear CLI, deterministic output, helpful errors, representative test run.

`assets/templates/`: add/preserve recurring plans, reports, scenario suites, scorecards, decision records. Valid when used by workflow, copied/filled by agent, rendered by script, or checked by validator; script consumption is optional. Obvious bounded template slots are fine in templates, but delivered targets must not contain unresolved scaffold markers.

`evals/` scenarios: add when activation/behavior quality matters. Types: `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`, `regression`, `adversarial`. Metrics are measured only after execution.

## Bounded Patch Rules

Patch one coherent batch; protect evaluator fixtures and expected outputs; preserve target-specific behavior; avoid generic disconnected resources; avoid whole-target rewrites unless unsalvageable; record changed files and validation commands. When support-resource integration is weak, classify before deleting and integrate useful assets through `SKILL.md`, references, validators, or workflow instructions.

## Common Fixes

- Generic description -> concrete triggers plus negative boundaries.
- Long `SKILL.md` -> move branches to linked references.
- No output contract -> mode-specific outputs.
- No validation -> gates, final checklist, deterministic validators.
- No scenarios -> planned suite plus runner/checklist.
- Unresolved scaffold files -> delete or replace scaffolding.
- Weakly integrated useful asset -> workflow reference, copy/fill rule, or path validation.
- Pure explanatory asset -> move to `references/`, then remove only after update.
- Host-specific semantics in the core -> move only installation/UI details to an adapter; keep shared behavior in portable `SKILL.md`/references/scripts.
- Mutable baseline/evaluator -> snapshot/freeze evidence before candidate mutation.
- Package writes directly to last-good output -> stage, validate, alias-check, commit atomically, and preserve recovery evidence.
- Claims without evidence -> evidence policy plus citations/measured outputs.
- Saturated benchmark -> keep gate and add auxiliary metric.
