---
name: skill-benchmark
description: use when asked to benchmark, audit, score, validate, compare, or measure maturity of reusable agent skills-compatible packages for chatgpt/openai, codex, claude, github copilot, cursor, or other compatible hosts. produces evidence-based reports with scorecard, gates, source/evaluator identities, scenario status, risks, improvements, portability findings, and verdict. use for report validation, version comparison, publish readiness, or metrics from validated scenario evidence. do not use for generic code review, skill mutation, prompt advice, or hardening unless the requested deliverable is a reusable skill benchmark.
---

# Skill Benchmark

## Purpose

Produce repeatable, host-neutral benchmark reports for reusable Agent Skills packages. Own evidence intake, static scoring, behavioral-result validation, report validation, version comparison, portability assessment, and verdicts. Do not edit/harden benchmark targets; route mutation to the owning workflow.

## Evidence model

Keep these evidence layers separate:

- **static**: inspected package structure/content;
- **behavioral**: executed or supplied scenario outcomes;
- **runtime**: host/tool execution evidence;
- **qualitative**: reviewer judgment that static checks cannot prove;
- **planned**: scenarios/evals that exist but were not executed;
- **blocked**: evidence unavailable because a required capability/input is missing.

Never turn planned, missing, stale, or unvalidated evidence into measured claims.

For filesystem benchmarks, prefer an immutable target snapshot and frozen evaluator identity. Strict before/after deltas require comparable target/evaluator/scenario identities. When the benchmark asks whether the skill adds value over the host baseline, use an optional `without-skill` control without replacing the immutable prior-version baseline for regression claims. Keep hidden evaluator assets outside candidate-visible execution inputs when claiming blind evaluation. Read [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md) and [`references/control-and-capability-delta.md`](references/control-and-capability-delta.md).

## Modes

| Mode | Use when | Required evidence | Output |
|---|---|---|---|
| `single-skill-benchmark` | one target needs maturity scoring | target package/content | scorecard + gates + evidence limits |
| `comparison-benchmark` | baseline and candidate must be compared, optionally with a no-skill control | separate frozen target identities + same evaluator/scenario identities; optional control arm | comparable deltas + capability delta |
| `report-validation` | an existing benchmark report must be checked | report file/text | validation findings |
| `behavioral-evidence-benchmark` | scenario outcomes are supplied/executed | schema-valid result evidence | metrics + provenance status |
| `portability-benchmark` | target claims multiple hosts | target + requested host profiles | portable-core/adapter findings |
| `template-only` | no inspectable target exists | missing-input list | report skeleton; no score |

## Host portability

Use the open Agent Skills package as the semantic core. Do not make benchmark behavior depend on ChatGPT-, Codex-, Claude-, Copilot-, Cursor-, or vendor-private tool names. `agents/openai.yaml` is an optional OpenAI adapter and must not add score merely by existing.

When portability matters, read [`references/host-portability.md`](references/host-portability.md). Resolve capabilities before execution rather than branching only on product name:

1. filesystem read;
2. writable work/output location outside protected target evidence;
3. Python 3.10+ or equivalent command execution;
4. optional independent scenario/evaluator execution;
5. artifact delivery.

Denote the resolved Python launcher/execution method as `<PYTHON>`; do not assume `python3`, Bash, POSIX utilities, or a specific sandbox path.

## Required inputs and protected evidence

Required: target content/path/source, benchmark mode, and report destination or inline-report choice. Optional: baseline, scenario results, prior reports, review notes, issue links, requested hosts.

Target content may be a skill folder, extracted `skill.zip`, pasted package content, or an already-generated benchmark report for validation. If target content is unavailable, return the [`references/report-template.md`](references/report-template.md) structure with missing inputs and no score/readiness claim.

Protect target files, fixtures, expected outputs, secrets, credentials, frozen evaluator/scenario inputs, generated baseline evidence, and read-only paths. Never alter them to make a benchmark pass.

## Progressive loading

Load only branch-relevant resources:

- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): portable commands, evidence hierarchy, comparison, paths, final response.
- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): dimensions, weights, gates, verdict rules.
- [`references/test-scenarios.md`](references/test-scenarios.md): versioned scenario evidence schema/formulas/statuses.
- [`references/report-template.md`](references/report-template.md): required report sections/order.
- [`references/host-portability.md`](references/host-portability.md): portable core, host profiles, capability rules.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): source snapshots, evaluator identity, alias safety, recovery, receipts.
- [`references/control-and-capability-delta.md`](references/control-and-capability-delta.md): no-skill control-arm rules, hidden-evaluator visibility, trace provenance, and deterministic capability-delta interpretation.
- [`references/evaluation-ladder-and-parent-comparison.md`](references/evaluation-ladder-and-parent-comparison.md): L0-L5 staged evaluation, direct-parent attribution, hard-gate-first comparison, and non-dominated multi-metric reporting.
- [`references/multi-candidate-evaluation.md`](references/multi-candidate-evaluation.md): identity/comparability contract for evaluating several search candidates without taking ownership of survivor selection.
- [`assets/templates/benchmark-report.md.template`](assets/templates/benchmark-report.md.template): manual report skeleton.
- [`assets/templates/scenario-results.json.template`](assets/templates/scenario-results.json.template): identity-bound behavioral results skeleton.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation/non-activation/ambiguous/edge/regression/adversarial coverage.
- [`examples/activation-scenarios.json`](examples/activation-scenarios.json): compact activation calibration examples.
- [`scripts/snapshot_target.py`](scripts/snapshot_target.py): capture/verify exact target bytes.
- [`scripts/benchmark_identity.py`](scripts/benchmark_identity.py): compute frozen evaluator identity.
- [`scripts/generate_benchmark_report.py`](scripts/generate_benchmark_report.py): portable deterministic report generator.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py): report/evidence validator.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py): scenario evidence validator.
- [`scripts/compare_benchmark_arms.py`](scripts/compare_benchmark_arms.py): compare candidate against immutable baseline and optional `without-skill` control using identity-bound behavioral evidence.
- [`scripts/validate_portability.py`](scripts/validate_portability.py): structural portability validator.
- [`scripts/package_skill.py`](scripts/package_skill.py): deterministic portable package builder with atomic receipt.


- `scripts/validate_candidate_set.py`: validates multi-candidate evidence; evolutionary-search contract v4 additionally freezes scoring-policy identity, candidate/parent identities, evaluation level, requires a non-empty comparable metric set, and validates metric uncertainty.
- `contracts/integration-manifest.json`: declares the benchmark multi-candidate evidence contract for cross-skill impact analysis.

## Workflow

### 1. Establish target and capabilities

1. Resolve exactly one target root containing `SKILL.md` when filesystem content exists.
2. Read target `SKILL.md` first; inventory relevant references/scripts/assets/examples/evals/adapters.
3. Select mode, requested hosts, `<PYTHON>`, writable work dir, protected paths, and behavioral evidence policy.
4. Keep benchmark outputs outside the target package.

### 2. Freeze source and evaluator identity

For filesystem targets, prefer:

```text
<PYTHON> scripts/snapshot_target.py capture --target <TARGET> --snapshot-dir <WORK>/target-snapshot --out <WORK>/target-manifest.json
<PYTHON> scripts/benchmark_identity.py --json <WORK>/evaluator-manifest.json
```

Benchmark the snapshot. Do not silently reopen a mutable live target for later scoring. If immutable snapshotting cannot be performed, label the report `live-unfrozen` and do not make strict version-delta claims.

### 3. Score static evidence

Use [`references/benchmark-rubric.md`](references/benchmark-rubric.md). Classify resources by role before penalizing/removing them. Useful integrated templates/assets are not worse than absence. Host-specific adapters are reported separately and do not receive portable-core bonus points.

When scripts can run:

```text
<PYTHON> scripts/generate_benchmark_report.py --target <SNAPSHOT_OR_TARGET> --source-manifest <WORK>/target-manifest.json --out <OUTPUT_ROOT> --hosts <HOSTS>
```

Omit `--source-manifest` only when no frozen snapshot exists; the report must then disclose `live-unfrozen` evidence.

### 4. Add behavioral evidence only after validation

Validate scenario evidence before metrics:

```text
<PYTHON> scripts/validate_scenario_results.py --results <RESULTS_JSON> --json-output <WORK>/scenario-validation.json
```

Require the v2 identity-bound envelope in [`references/test-scenarios.md`](references/test-scenarios.md). Record `arm_type`, trace identity when available, and evaluator visibility/leakage status when hidden graders or holdouts are used. Reject top-level arrays and any unversioned scenario-result shape.

Never invent activation precision/recall, robustness, output conformance, criteria coverage, quality scores, or rework rate.

### 5. Compare versions only when comparable

When iterative optimization supplies a direct parent, preserve both roles: compare candidate vs parent for local transformation attribution and candidate vs stable baseline for cumulative regression. When a caller supplies multiple search candidates, follow `references/multi-candidate-evaluation.md`: evaluate each against the same frozen identities and emit comparable per-candidate evidence, but leave survivor/Pareto selection to the caller/search controller. Use `references/evaluation-ladder-and-parent-comparison.md`; do not replace the baseline with the parent silently.

For self-improvement, treat controller identity as generation provenance rather than a benchmark arm. Baseline/candidate strict deltas require the same generation/controller provenance in addition to the same evaluator, suite, and materially relevant host configuration.

For `comparison-benchmark`:

1. freeze baseline and candidate separately;
2. require the same evaluator identity;
3. require the same scenario suite/evidence contract for behavioral deltas;
4. compare like-for-like dimensions/metrics only;
5. optionally add a `without-skill` arm when the question is incremental skill value rather than only regression safety;
6. keep the prior-version baseline as the primary regression baseline for existing-skill updates;
7. reject blind/hidden-evaluator claims when candidate execution could read evaluator-only assets;
8. if evaluator/scenario/host configuration identities differ materially, show standalone results and label delta `not comparable`.

When arm files are available, run:

```text
<PYTHON> scripts/compare_benchmark_arms.py --candidate <CANDIDATE_RESULTS> [--baseline <BASELINE_RESULTS>] [--parent <PARENT_RESULTS>] [--without-skill <CONTROL_RESULTS>] --json-output <WORK>/arm-comparison.json
```

A higher score from a changed rubric is not evidence that the skill improved. A no-skill control is not a substitute for the prior-version baseline when regression claims are being made.

### 6. Add qualitative review without disguising judgment

Use the rubric/report template to review contradictions, stale/volatile knowledge, resource usefulness, and semantic completeness. Mark these findings as qualitative/observed/inferred. Static scanners must leave unprovable gates as `review`, not auto-pass them.

### 7. Validate, reverify, and finalize

For a generated report:

```text
<PYTHON> scripts/validate_benchmark_report.py --report <REPORT_MD> --json-output <WORK>/report-validation.json
```

When a target snapshot exists, verify it before final readiness/comparison claims:

```text
<PYTHON> scripts/snapshot_target.py verify --manifest <WORK>/target-manifest.json --json <WORK>/target-verification.json
```

If the live source changed, either keep evaluating the frozen snapshot or explicitly invalidate/re-baseline. Do not mix versions.

After report validation and source/evaluator verification pass, apply the **freeze after pass** (`freeze-after-pass`) gate: freeze the benchmark evidence used for the final claim. Do not edit the accepted report, frozen target snapshot, evaluator inputs, or scenario evidence afterward. Any such edit invalidates finalization and requires rerunning the affected gates.

Generated report+receipt and package+receipt delivery must be atomic when filesystem writes are available: stage all outputs, validate them, commit together, preserve the last-known-good outputs on failure, and retain explicit recovery evidence if rollback is incomplete. Read [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md).

## Output contract

When staged evaluation metadata is supplied, report the highest evaluation level actually supported by evidence and do not imply higher levels ran. When a direct parent is supplied, report parent identity and candidate-vs-parent delta separately from candidate-vs-baseline. Apply hard gates before any score-based comparison; if multiple candidates are non-dominated and no frozen weighting policy exists, report that rather than manufacturing an overall winner.


A substantive benchmark must include:

- target name/source and source evidence state;
- target tree identity and evaluator identity when filesystem evidence exists;
- inspected and missing evidence;
- 0-100 scorecard and rubric dimensions;
- gate statuses including unresolved qualitative review gates;
- static inventory/resource integration;
- behavioral metrics labeled `measured`, `supplied`, `planned`, `blocked`, or `not measured`;
- scenario coverage across activation/non-activation/ambiguous/edge cases;
- portability result when requested/claimed;
- evidence-based findings, risks, prioritized improvements;
- verdict (`approve`, `approve with reservations`, `reject`);
- commands/outcomes and residual risks;
- explicit non-comparability statement when evaluator/scenario/host identity differs materially;
- control-arm status, capability delta, trace provenance, and evaluator-visibility/leakage status when those evidence surfaces are used.

## Stop conditions

Stop before scoring/finalizing when:

- target is missing/unreadable or filesystem target lacks root `SKILL.md`;
- multiple roots are ambiguous;
- request requires target mutation under benchmark-only scope;
- measured behavioral claims are requested without valid result evidence;
- strict comparison lacks stable baseline/candidate/evaluator/scenario identity;
- a hidden/blind evaluator claim is requested but evaluator-only assets were visible to the evaluated candidate or leakage status is unknown;
- report would cite uninspected files;
- output aliases target/protected evidence/receipt;
- scenario evidence is malformed or identity-conflicted;
- required portability claim depends on host-private core behavior;
- generated report validation fails and cannot be corrected from available evidence.

## Validation and finalization

Before completion confirm: stable target identity or explicit `live-unfrozen` limitation; evaluator identity for strict comparisons; required report sections; visible failed/review gates; metric-status distinctions; local references resolve; useful resources are not penalized merely for existing; requested-host portability is separated from runtime support; report validator passes when runnable; scenario validator passes before behavioral metrics are used; arm comparison validation passes before capability-delta claims; hidden-evaluator visibility/leakage evidence supports any blind-evaluation claim; accepted evidence is frozen after the final pass; atomic delivery/last-known-good recovery gates passed when files were written; no target/evaluator/report/scenario edit occurred after frozen evidence was accepted.

Report generated paths/content, commands, score, gate status, source/evaluator identities, behavioral evidence status, portability status, missing evidence, and residual risks. If an applicable hard gate did not run or failed, do not claim readiness/completion beyond the evidence actually established.
