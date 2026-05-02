---
name: skill-benchmark
description: use when asked to benchmark, audit, score, validate, compare, or measure maturity of reusable chatgpt, claude, copilot, codex, or compatible agent skill packages, target skills, and benchmark reports. produces evidence-based markdown reports with scorecard, gates, inventory, scenario status, risks, improvements, and verdict. use for report validation, version comparison, publish readiness, or metrics from validated scenario results. do not use for generic code review, product planning, prompt advice, document writing, skill creation, or hardening unless the deliverable is a reusable skill benchmark.
---

# Skill Benchmark

## Purpose

Produce repeatable benchmark reports for reusable skill packages. Own evidence intake, static scoring, optional behavioral-result validation, report validation, comparison, and verdicts. Do not edit or harden targets; route mutation to the owning workflow.

## Activation and boundaries

Use for benchmark, audit, scorecard, maturity assessment, report validation, version comparison, publish-readiness, standardized reports, or evidence review for ChatGPT, Claude, Copilot, Codex, or compatible agent skill packages.

Strong triggers: benchmark/score/audit this skill; validate this benchmark report; compare skill versions; measure maturity; decide publish readiness; generate a skill benchmark report; calculate activation precision/recall, output conformance, robustness, or rework rate from supplied scenario results.

Do not use for generic code review, product planning, prompt advice, document writing, skill creation, repository refactoring, explaining skills, or target hardening unless the requested deliverable is a reusable skill benchmark.

## Scope and required inputs

Required input: target content or report text/path, target identity/source, mode, and output location or inline report choice. Optional: baseline version, scenario results, prior reports, review notes, issue links, or expected activation cases.

Target content may be a skill folder, extracted `skill.zip`, pasted package text, or enough inspected text to evaluate. Current target files and command output are primary evidence. Supplied scenario results become measured evidence only after schema validation. Proposed prompts and bundled evals remain planned evidence until executed. If target content is unavailable, return the [`references/report-template.md`](references/report-template.md) structure with missing inputs and no inspection, score, or readiness claims.

Protected: fixtures, expected outputs, secrets, credentials, read-only paths, generated evidence, and benchmark baselines. Never overwrite them to make a report pass.

## Mode matrix

| Mode | Use when | Required evidence | Output |
|---|---|---|---|
| `single-skill-benchmark` | one target skill needs maturity scoring | target package or inspectable text | scored report plus gates |
| `comparison-benchmark` | target and baseline must be compared | separate target/baseline evidence | comparable deltas only |
| `report-validation` | an existing benchmark report must be checked | report path/text | pass/fail findings |
| `behavioral-evidence-benchmark` | scenario results are supplied | schema-valid results | measured metrics plus static review |
| `template-only` | no inspectable target exists | missing-input list | skeleton; no score |

## Progressive loading

Load only branch-relevant resources:

- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): commands, paths, evidence hierarchy, comparison, final response.
- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): dimensions, scoring bands, gates, verdict thresholds.
- [`references/test-scenarios.md`](references/test-scenarios.md): scenario schema, formulas, statuses, measurement rules.
- [`references/report-template.md`](references/report-template.md): required report sections/order.
- [`assets/templates/benchmark-report.md.template`](assets/templates/benchmark-report.md.template): manual report skeleton.
- [`assets/templates/scenario-results.json.template`](assets/templates/scenario-results.json.template): result JSON skeleton.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, edge, regression, adversarial coverage.
- [`examples/activation-scenarios.json`](examples/activation-scenarios.json): compact calibration examples for activation boundaries.
- [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js): deterministic report generator.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py): report validator.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py): behavioral result validator.
- [`scripts/package_skill.py`](scripts/package_skill.py): package/archive validator for this skill's `skill.zip`.

## Workflow

1. Locate target. Read target `SKILL.md` first; confirm one root `SKILL.md` when possible; inventory `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`; record inspected files.
2. Select mode and evidence policy. Keep static, behavioral, supplied, planned, and blocked evidence separate.
3. Classify resources before scoring or deletion advice. `references/` hold guidance/schemas/rubrics/rules; `assets/templates/` hold reusable skeletons. Do not reward deleting useful templates/assets to raise a static score.
4. For filesystem targets, run [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js) with `--target` and optional `--out`; keep reports outside the target package unless the caller repo explicitly owns them. See [`references/benchmark-workflow.md`](references/benchmark-workflow.md).
5. Add behavioral evidence only when supplied or executed. Validate JSON with [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py), apply [`references/test-scenarios.md`](references/test-scenarios.md), and never invent precision, recall, robustness, output conformance, criteria coverage, or rework rate.
6. Enrich with qualitative review using [`references/benchmark-rubric.md`](references/benchmark-rubric.md) and [`references/report-template.md`](references/report-template.md). Separate automated static findings, behavioral findings, reviewer judgment, and missing evidence.
7. Validate/finalize with [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) when a report file exists. Confirm required sections, visible failed gates, no scaffold markers, and evidence-backed measured metrics.

## Output contract

Benchmark responses/reports must include target name/path/source; inspected and missing evidence; 0-100 scorecard; gates; static inventory; behavioral metrics marked measured, supplied, planned, blocked, or not measured; activation, non-activation, ambiguous, and edge prompts; findings, risks, improvements; suggested description when relevant; verdict (`approve`, `approve with reservations`, or `reject`); validation commands/outcomes; explicit not-measured statement when no executed/supplied scenario evidence exists.

## Stop conditions

Stop before scoring/finalizing when the target is missing, unreadable, or lacks root `SKILL.md`; multiple roots are ambiguous; the request requires target mutation under benchmark-only scope; measured behavioral metrics are requested without valid results; the report would cite uninspected files; output would overwrite protected paths; scenario evidence is malformed; or generated report validation fails and cannot be corrected from available evidence.

## Validation rules

Before completion, confirm stable target identity; inspected or unavailable `SKILL.md`; all [`references/report-template.md`](references/report-template.md) sections; visible failed gates; metric status distinctions; every named local resource exists or is clearly an external output path; asset/template findings distinguish absent, integrated, unreferenced, and obsolete scaffold files; useful integrated assets are not penalized versus absence; [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) passes when runnable; [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py) passes before scenario data becomes measured evidence.

## Finalization

Report inspected files, generated paths, commands run, score, gate status, missing evidence, and residual risks. If validation fails, do not claim completion; return the partial report and failed gates.
