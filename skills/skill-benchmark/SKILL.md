---
name: skill-benchmark
description: use when asked to benchmark, audit, score, validate, compare, or measure maturity of a chatgpt, claude, copilot, codex, or agent skill package and produce an evidence-based markdown benchmark report with scorecard, gates, inventory, scenario suite, behavioral metrics, risks, prioritized improvements, and verdict. use report-validation mode for existing benchmark reports and comparison mode for two versions. do not use for generic code review, product planning, prompt advice, document writing, skill creation, or target package hardening unless the requested output includes a reusable skill benchmark.
---

# Skill Benchmark

## Purpose

Generate a measurable, standardized, and repeatable benchmark report for a reusable skill package. This skill owns benchmark evidence, scoring, report validation, and comparison. It does not own editing or hardening the benchmarked package; when the user asks for improvement work, first produce or preserve the benchmark evidence and clearly separate any later mutation work from the benchmark result.

## Activation boundary

Use this skill when the requested deliverable is a benchmark, audit, scorecard, maturity assessment, validation report, or comparison for a ChatGPT, Claude, Copilot, Codex, or compatible agent skill package.

Strong triggers include:

- benchmark this skill, score this skill, audit this skill package, validate this benchmark report, compare these skill versions, measure skill maturity, generate a skill benchmark report, or decide whether this skill is ready to publish;
- requests for a standardized markdown report with score, gates, inventory, scenarios, risks, and prioritized improvements;
- review of supplied scenario results where activation precision, recall, output conformance, robustness, or rework rate must be calculated from evidence.

Do not use this skill for generic code review, product planning, prompt advice, document writing, skill creation from scratch, ordinary repository refactoring, or explaining how skills work unless the user explicitly asks for a reusable skill benchmark deliverable. Do not use this skill as the primary workflow when the user only asks to edit or harden a target package; use a hardening or harness workflow and keep benchmark output as evidence.

## Scope boundaries and assumptions

Operate only on benchmark evidence and benchmark report artifacts. Treat target package edits, repository implementation, generic prompt rewrites, and hardening work as out of scope unless another workflow explicitly owns those changes. Do not overwrite protected fixtures, expected outputs, secrets, credentials, or user-declared blocked paths.

Assume behavioral metrics are unknown until scenario prompts are executed or the user supplies validated result evidence. If static scores are saturated, preserve the score as a gate and use an auxiliary metric such as scenario conformance, evidence completeness, or validator coverage before claiming improvement.

## Required inputs

Resolve these inputs from the user request or available filesystem before generating a benchmark:

1. Target content: a skill folder, extracted `skill.zip`, pasted skill contents, or enough target content to inspect.
2. Target identity: target skill name and inspected path or source description.
3. Benchmark mode: single skill, comparison, report validation, behavioral evidence, or template-only.
4. Optional evidence: prior outputs, scenario results, expected activation cases, issue links, review notes, user feedback, or an older benchmark report.
5. Optional comparison baseline: previous skill version, previous benchmark report, or another skill package.
6. Output location when files can be written; otherwise return report content in the response.

If target content is unavailable, return the report structure from [`references/report-template.md`](references/report-template.md), list the missing inputs, and do not claim inspection or scoring evidence.

## Mode selection

| User intent | Mode | Required inputs | Primary output | Closure check |
|---|---|---|---|---|
| Benchmark one skill package | `single-skill-benchmark` | target package or contents | canonical markdown benchmark report | report validator passes or limitations are stated |
| Compare two versions or packages | `comparison-benchmark` | target plus baseline | benchmark report with delta section | evidence sets are separated and only comparable deltas are claimed |
| Validate an existing report | `report-validation` | report path or report text | pass/fail findings and fixes | [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) when filesystem access is available |
| Use supplied scenario results | `behavioral-evidence-benchmark` | target plus result json or table | benchmark with measured metrics | result schema is validated before metrics are treated as measured |
| No inspectable target | `template-only` | target name or benchmark intent | report template and missing-input list | no claims of inspection are made |

## Progressive loading

Load only what the branch needs:

- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): command sequence, evidence handling, path rules, and finalization workflow.
- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): score dimensions, scoring bands, maturity classification, and gate interpretation.
- [`references/test-scenarios.md`](references/test-scenarios.md): scenario schema, behavioral metric formulas, and measured-versus-planned rules.
- [`references/report-template.md`](references/report-template.md): required final report structure and section contract.
- [`assets/templates/benchmark-report.md.template`](assets/templates/benchmark-report.md.template): reusable markdown skeleton when a report must be drafted manually.
- [`assets/templates/scenario-results.json.template`](assets/templates/scenario-results.json.template): reusable scenario result skeleton when collecting execution evidence.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, edge, regression, and adversarial coverage for this skill package.
- [`examples/hardening-scenarios.json`](examples/hardening-scenarios.json): example legacy result-style scenario records for benchmark review.
- [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js): deterministic report generator for filesystem targets.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py): deterministic report quality validator.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py): deterministic validator for supplied behavioral result json.
- [`scripts/package_skill.py`](scripts/package_skill.py): package and archive validator used when this skill package itself must be delivered as `skill.zip`.

## Workflow

1. Locate and inspect the target skill.
   - Read the target `SKILL.md` first.
   - Confirm the target has exactly one root `SKILL.md` when filesystem access is available.
   - List the package tree and identify `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, and `evals/` if present.
   - Record which files were actually inspected.

2. Select the benchmark mode and evidence policy.
   - Use the mode table above.
   - Treat target files and command output from the current run as primary evidence.
   - Treat supplied scenario results as measured only after schema validation.
   - Treat proposed scenario prompts as planned until executed.

3. Classify supporting resources before scoring or recommending deletion.
   - Treat `references/` as conditional guidance, schemas, rubrics, or rules.
   - Treat `assets/templates/` as reusable artifact skeletons that may be copied, filled, or rendered.
   - Do not treat references and templates as interchangeable merely because their topics overlap.
   - Do not recommend removing a useful template, asset, example, script, or reference solely to improve a static score. Prefer integration through workflow references, script usage, or validation coverage.

4. Generate static benchmark evidence when a filesystem target is available.
   - Run [`scripts/generate_benchmark_report.js`](scripts/generate_benchmark_report.js) with `--target` and, when needed, `--out`.
   - Keep generated reports outside the target skill package unless the surrounding repository explicitly owns benchmark reports.
   - Use [`references/benchmark-workflow.md`](references/benchmark-workflow.md) for command details and path decisions.

5. Add behavioral evidence only when available.
   - Validate supplied result json with [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py) before calculating metrics.
   - Apply [`references/test-scenarios.md`](references/test-scenarios.md) for formulas and status labels.
   - Do not invent activation precision, recall, robustness, output conformance, criteria coverage, or rework rate.

6. Enrich the report with qualitative review.
   - Apply [`references/benchmark-rubric.md`](references/benchmark-rubric.md) to score dimensions and gates.
   - Apply [`references/report-template.md`](references/report-template.md) as the required structure.
   - Clearly separate automated static findings, behavioral findings, and reviewer judgment.

7. Validate and finalize.
   - Run [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) on any generated report when filesystem access is available.
   - Confirm all required sections exist, no unresolved scaffold markers remain, and measured metrics are backed by execution evidence.
   - Return the report path or report content, command outcomes, failed gates, missing evidence, and residual risks.

## Output contract

A benchmark response or report must include:

1. Target skill name and inspected path or source description.
2. Evidence sources and explicit missing evidence.
3. Scorecard on a 0 to 100 scale using the bundled rubric.
4. Gate evaluation with pass/fail status and evidence.
5. Static structure inventory.
6. Behavioral metrics, marked measured, supplied, planned, blocked, or not measured.
7. Scenario suite with activation, non-activation, ambiguous, and edge-case prompts.
8. Evidence-based findings, risks, and prioritized improvements.
9. Suggested improved activation description when relevant.
10. Verdict: approve, approve with reservations, or reject.
11. Validation commands executed and outcomes when commands were available.
12. Clear statement that scenario metrics are not measured when no executed or supplied scenario evidence exists.

## Stop conditions

Stop and report a blocker before scoring or finalizing when:

- The target path is missing, unreadable, or contains no root `SKILL.md`.
- More than one possible target skill root is present and the user did not identify which one to benchmark.
- The request would require changing the target package when the user only asked for a benchmark.
- The user asks for measured behavioral metrics but no scenario execution results are available.
- The report would need to cite files that were not inspected.
- The output path would overwrite protected fixtures, expected outputs, secrets, credentials, or user-declared read-only paths.
- Supplied scenario result evidence is malformed and cannot support requested metrics.
- The generated report fails validation and cannot be corrected within the available evidence.

## Validation rules

Before declaring a benchmark complete:

- The target identity is stable and reproducible.
- `SKILL.md` frontmatter and body were inspected or explicitly unavailable.
- All required report sections from [`references/report-template.md`](references/report-template.md) are present.
- Failed gates are not hidden by a high numerical score.
- Behavioral metrics distinguish measured, supplied, planned, blocked, and not measured evidence.
- Every local resource named in the report exists or is clearly described as an output path rather than a bundled reference.
- Asset/template findings distinguish absent assets, integrated operational templates, unreferenced assets, and obsolete scaffold files. Absence of assets is not scored as better than useful integrated assets.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py) passes when a report file exists and the script can run.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py) passes before scenario results are used as measured behavioral evidence.

## Finalization checklist

Report exactly what was done: inspected files, generated paths, commands executed, score, gate status, missing evidence, and residual risks. If validation fails, do not claim the benchmark is complete; return the partial report and the failed gates.
