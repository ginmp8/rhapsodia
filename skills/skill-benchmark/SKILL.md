---
name: skill-benchmark
description: use when asked to benchmark, audit, score, validate, compare, or measure maturity of chatgpt, claude, copilot, codex, or compatible agent skill packages by producing an evidence-based markdown report with scorecard, gates, inventory, scenarios, behavioral metrics, risks, improvements, and verdict. use report-validation for existing reports and comparison for two versions. do not use for generic code review, product planning, prompt advice, document writing, skill creation, or hardening unless a reusable skill benchmark is the requested artifact.
---

# Skill Benchmark

## Purpose

Produce measurable, repeatable benchmark reports for reusable skill packages. Own evidence, scoring, report validation, comparison, and verdicts. Do not edit or harden the target; preserve benchmark evidence and route later mutation work to its owning workflow.

## Activation

Use when the requested artifact is a benchmark, audit, scorecard, maturity assessment, validation report, comparison, publish-readiness decision, standardized markdown report, or evidence review for a ChatGPT, Claude, Copilot, Codex, or compatible agent skill package.

Strong triggers: benchmark/score/audit this skill, validate this benchmark report, compare skill versions, measure maturity, generate a skill benchmark report, decide publish readiness, or calculate activation precision/recall, output conformance, robustness, or rework rate from supplied results.

Do not use for generic code review, product planning, prompt advice, document writing, skill creation from scratch, repository refactoring, explaining how skills work, or target hardening unless the deliverable is a reusable skill benchmark. For edit/hardening-only work, use the owning hardening/harness workflow and keep benchmark output as evidence.

## Scope, inputs, assumptions

- Scope: benchmark evidence and report artifacts only. Out of scope unless another workflow owns it: target edits, implementation, generic prompt rewrites, hardening.
- Protected: fixtures, expected outputs, secrets, credentials, user-declared read-only paths.
- Required inputs: target content, target identity/path/source, mode, optional evidence, optional baseline, output location or inline report.
- Target content may be a skill folder, extracted `skill.zip`, pasted content, or enough text to inspect.
- Optional evidence includes prior outputs, scenario results, expected activation cases, issue links, review notes, feedback, or older benchmark reports.
- Behavioral metrics stay unknown until prompts are executed or supplied results pass schema validation.
- If static scores saturate, keep the score as a gate and use scenario conformance, evidence completeness, or validator coverage before claiming improvement.
- If target content is unavailable, return the structure from [`references/report-template.md`](references/report-template.md), list missing inputs, and do not claim inspection or scoring.

## Modes

- `single-skill-benchmark`: target -> canonical markdown report; validator passes or limitations stated.
- `comparison-benchmark`: target + baseline -> delta report; evidence stays separated; claim only comparable deltas.
- `report-validation`: report path/text -> pass/fail findings/fixes; run [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) when files exist.
- `behavioral-evidence-benchmark`: target + result JSON/table -> measured metrics only after schema validation.
- `template-only`: no inspectable target -> template and missing-input list; no inspection claims.

## Progressive loading

Load only branch-relevant resources:

- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): commands, evidence hierarchy, paths, final response.
- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): dimensions, bands, maturity classes, gates.
- [`references/test-scenarios.md`](references/test-scenarios.md): scenario schema, formulas, status labels.
- [`references/report-template.md`](references/report-template.md): required report sections and order.
- [`assets/templates/benchmark-report.md.template`](assets/templates/benchmark-report.md.template): manual report skeleton.
- [`assets/templates/scenario-results.json.template`](assets/templates/scenario-results.json.template): scenario result skeleton.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, edge, regression, adversarial coverage.
- [`examples/hardening-scenarios.json`](examples/hardening-scenarios.json): legacy result examples.
- [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js): deterministic report generator.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py): report validator.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py): behavioral result validator.
- [`scripts/package_skill.py`](scripts/package_skill.py): package/archive validator when this skill itself is delivered as `skill.zip`.

## Workflow

1. Locate target. Read target `SKILL.md` first; confirm exactly one root `SKILL.md` when possible; inventory `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`; record inspected files.
2. Select mode/evidence policy. Current target files and command output are primary evidence. Supplied scenario results are measured only after schema validation; proposed prompts are planned.
3. Classify resources before scoring or deletion recommendations. `references/` are guidance/schemas/rubrics/rules; `assets/templates/` are reusable skeletons. Do not treat them as interchangeable or delete useful resources only to raise a static score; prefer workflow integration, script usage, or validation coverage.
4. For filesystem targets, run [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js) with `--target` and optional `--out`. Keep reports outside the target package unless the caller repo explicitly owns them. See [`references/benchmark-workflow.md`](references/benchmark-workflow.md).
5. Add behavioral evidence only when available. Validate JSON with [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py), apply [`references/test-scenarios.md`](references/test-scenarios.md), and never invent precision, recall, robustness, output conformance, criteria coverage, or rework rate.
6. Enrich with qualitative review using [`references/benchmark-rubric.md`](references/benchmark-rubric.md) and [`references/report-template.md`](references/report-template.md). Separate automated static findings, behavioral findings, and reviewer judgment.
7. Validate/finalize. Run [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) on generated reports when available. Confirm required sections, no scaffold markers, and evidence-backed measured metrics. Return report path/content, command outcomes, failed gates, missing evidence, residual risks.

## Output contract

Benchmark responses/reports must include target name/path/source; evidence and missing evidence; 0-100 rubric scorecard; gate evaluation with evidence; static inventory; behavioral metrics marked measured, supplied, planned, blocked, or not measured; scenario suite with activation, non-activation, ambiguous, and edge-case prompts; findings, risks, prioritized improvements; suggested improved activation description when relevant; verdict (`approve`, `approve with reservations`, or `reject`); validation commands/outcomes; and an explicit not-measured statement when no executed/supplied scenario evidence exists.

## Stop conditions

Stop before scoring/finalizing when the target is missing, unreadable, or has no root `SKILL.md`; multiple roots are ambiguous; the request requires target mutation under benchmark-only scope; measured behavioral metrics are requested without results; the report would cite uninspected files; output would overwrite protected fixtures, expected outputs, secrets, credentials, or read-only paths; scenario evidence is malformed; or generated report validation fails and cannot be corrected from available evidence.

## Validation rules

Before completion, confirm stable target identity; inspected or explicitly unavailable `SKILL.md` frontmatter/body; all [`references/report-template.md`](references/report-template.md) sections; visible failed gates; metric status distinctions among measured, supplied, planned, blocked, and not measured; every named local resource exists or is clearly an output path; asset/template findings distinguish absent, integrated, unreferenced, and obsolete scaffold files; useful integrated assets are not penalized versus absence; [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) passes when runnable; [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py) passes before scenario data becomes measured evidence.

## Finalization

Report inspected files, generated paths, commands run, score, gate status, missing evidence, and residual risks. If validation fails, do not claim completion; return the partial report and failed gates.
