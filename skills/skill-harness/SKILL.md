---
name: skill-harness
description: use to design, run, audit, validate, package, or apply evidence-based harnesses for existing ChatGPT or agent skill packages. Supports auto/context/full modes; audit-only/plan-only/apply/validation-only/package mutation; skill folders or extracted zips; approved research; scenarios, metrics, gates, validators, reports, bounded edits, comparison, and skill.zip packaging. Do not use for generic code, normal docs/reports, product planning, prompt advice, skill creation, or skill explanations.
---

# Skill Harness

## Purpose

Build a controlled evidence harness around an existing ChatGPT or Agent skill so it can be audited, improved, validated, compared, and packaged without ad hoc rewriting. Owns reusable skill-package work across `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `evals/`, scenarios, validators, reports, and packaging hygiene.

## Activate / Do Not Activate

Use when the user asks to inspect, audit, harden, benchmark, validate, package, or harness an existing skill package; make evidence-backed edits to a skill folder or extracted zip; define activation/non-activation scenarios, edge cases, metrics, gates, evaluators, validators, reports, or packaging checks; or compare baseline/final skill quality after bounded edits.

Do not use for generic code review, application refactors, CI work, repository implementation outside a reusable skill, one-off prompt writing/advice without a target skill package, ordinary document/slide/spreadsheet/report generation outside the skill package, creating skills, explaining ChatGPT skills, or unbounded autonomous work without target, scope, blocked paths, and gates. Use skill-creator for net-new skills or skill explanations.

## Inputs, Defaults, and Boundaries

Before mutating, resolve or infer:

- `TARGET_SKILL_PATH`: folder or extracted zip containing exactly one target skill.
- Harness mode: `auto`, `context`, or `full`.
- Mutation mode: `audit-only`, `plan-only`, `apply`, `validation-only`, or `package`.
- Writable scope: target skill folder only unless user changes it.
- Blocked: secrets, `.git`, evaluator fixtures, expected outputs, generated baseline evidence, benchmark baselines, user-declared read-only paths.
- Evidence policy: target files, supplied context, approved research, internal sources, or repository truth.
- Gates: valid structure, no unresolved scaffold markers, references exist, deterministic validators pass, package validation passes when packaging, target-specific tests pass when present.
- Final expectation: report only, applied edits, validation result, or `skill.zip`.

Default for "improve this skill": `mode=auto`, `mutation=apply`, target-only edits, protected fixtures/secrets, baseline first, one bounded improvement batch, validation, and package only when requested or clearly expected.

## Mode Selection and Mutation Rights

Harness modes:

- `auto`: inspect target first; research only concrete weaknesses; output harness plan plus bounded improvements.
- `context`: use only target contents and supplied context; output constrained changes and validation evidence.
- `full`: combine target evidence, user context, and approved current primary sources; resolve conflicts; output comprehensive harness run and package decision.

If research is forbidden, use `context` behavior.

Mutation modes:

- `audit-only`: inventory, audit score, findings, missing components, prioritized improvements; no edits.
- `plan-only`: harness map, evidence policy, proposed files, gates, sequence; no edits.
- `apply`: edits within allowed scope, validation evidence, before/after comparison, risks.
- `validation-only`: pass/fail gates, commands, evidence paths, blockers, remediation; no edits unless explicitly allowed.
- `package`: validated `skill.zip`, package evidence, exclusions, rollback notes; edit only as needed to pass gates.

## Resources and Progressive Loading

Always read target `SKILL.md` first. Load branch resources only as needed:

- `references/harness-principles.md`: decision statements, harness map, components, evidence, scenario coverage.
- `references/mode-research-policy.md`: source rules, conflicts, research restrictions.
- `references/skill-improvement-playbook.md`: bounded package changes.
- `references/evaluation-and-gates.md`: scores, gates, saturated metrics, readiness decisions.
- `references/scenario-suite-guidelines.md`: activation, ambiguous, edge, regression, adversarial scenarios.
- `references/report-contract.md`: final/durable reports.
- `references/cli-and-packaging-contract.md`: command contracts, package exclusions, exits.
- `assets/templates/harness-plan.md.template`, `assets/templates/harness-report.md.template`, `assets/templates/scenario-suite.json.template`: default plan, report, and planned-suite shapes.
- `scripts/skill_harness_inventory.py`, `scripts/skill_harness_audit.py`, `scripts/skill_harness_validate.py`, `scripts/skill_harness_package.py`: inventory, audit, validate, package.
- `examples/harness-hardening-cases.md`: activation/boundary examples for human review.

Templates are operational when copied, filled, rendered, validated, or declared in workflow. Do not remove useful templates merely because no script reads them. Keep this file as control plane; keep detailed rubrics, schemas, examples, and script contracts in references/examples.

## Harness Map

Define before editing: decision; object under test; writable/read-only/blocked scope; dependencies; activation, non-activation, ambiguous, edge, regression, adversarial scenarios; evidence; runner commands; evaluators; metrics; gates; evidence record for baseline, plan, changes, commands, outputs, final comparison, package path, risks.

## Workflow

1. Inspect: read target `SKILL.md`; confirm exactly one `SKILL.md`; list `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`; run inventory:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
```

2. Baseline: run static audit before planning:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
```

Treat score as structural evidence, not a substitute for domain judgment, scenarios, target tests, or packaging validation. If saturated, define auxiliary metrics before claiming improvement.

3. Evidence policy: `auto` derives research questions from observed weaknesses; `context` uses target plus supplied context only; `full` combines context with approved research. Record used/excluded sources, conflicts, unknowns.
4. Plan: use `assets/templates/harness-plan.md.template` unless a lighter inline plan is requested. Cover control plane, references, scripts, templates/assets, scenarios, validation, packaging, evidence, hypotheses, gates.
5. Apply bounded improvements: preserve target-specific behavior; edit only allowed paths; move long rules to linked references; add scripts only for deterministic heavy tasks; add scenario suites only when behavior evidence matters and user permits files; integrate templates/resources by workflow reference, script consumer, validator, or copy/fill instruction; classify weak resources before deletion; never invent facts, benchmark results, scenario pass rates, validation evidence, install state, or package state.
6. Validate and compare: re-run inventory/audit, run validator, syntax-check added/modified scripts, run target validators/tests when present, package when requested, and compare baseline/final including auxiliary metrics when scores are saturated.

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --output <report-dir>/validation.json
```

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json
```

7. Report/package: use `assets/templates/harness-report.md.template` for durable reports. Include mode, target, decision, sources, baseline score, plan, changes, commands, comparison, gates, risks, package path. Return a package path only when `skill.zip` exists and package report succeeds.

## Stop Conditions

Stop before editing when target lacks exactly one `SKILL.md`; target is not a ChatGPT/Agent skill package; `context` mode lacks required context; user requests external research under `context`; changes would touch secrets, `.git`, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, or user-blocked paths; improvement requires unsupported domain facts; or validation fails after structural changes and cannot be fixed within scope.

## Finalization and Output Contracts

Before success claims, verify: baseline inventory/audit ran; mode/evidence policy followed; harness map existed before edits; each added resource is referenced, script-consumed, validator-covered, or intentionally retained as an operational asset; scaffold markers absent; modified scripts run or are reported untested; gates evaluated truthfully; measured facts are separate from proposed scenarios/assumptions; blocked paths unchanged; package path is real when package mode is claimed.

Final response/report includes: mode/target, decision, evidence policy/sources, baseline inventory/audit gates, harness plan, changes, validation commands/outcomes, before/after comparison, auxiliary metrics when static score is saturated, risks/assumptions, recommendation, and package/artifact path only when valid.
