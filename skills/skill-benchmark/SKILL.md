---
name: skill-benchmark
description: "use when the requested deliverable is a reusable Agent Skills benchmark: maturity score/report, version or candidate comparison, report validation, behavioral-evidence interpretation, publish-readiness assessment, or portability benchmark across compatible hosts. produces evidence-bound scorecards, gates, source/evaluator identities, scenario status, risks, portability findings, and verdicts. do not use to mutate or harden a skill, perform generic code/prompt review, or choose search/evolution survivors; route those to the owning workflow."
---

# Skill Benchmark

## Mission and boundary

Benchmark reusable Agent Skills packages with repeatable, host-neutral evidence. Own evidence intake, static maturity scoring, validation of supplied/executed behavioral results, report validation, version/candidate comparison, portability assessment, and benchmark verdicts. Stay read-only with respect to benchmark targets: never edit or harden the skill being scored.

## Activation and routing

Use this skill when the user needs one of these benchmark deliverables:

- a 0-100 maturity scorecard and verdict for one existing skill;
- a comparable baseline/candidate or parent/candidate benchmark;
- validation of an existing benchmark report;
- interpretation of schema-valid behavioral scenario results;
- a portability benchmark across requested Agent Skills hosts;
- a publish/readiness assessment whose conclusion must be tied to inspected evidence.

Do not use for target mutation, iterative repair/hardening, generic code review, prompt advice, benchmark-fixture editing, or survivor/Pareto selection across search candidates. `skill-benchmark` may evaluate multiple candidates under one frozen contract, but the caller/search controller owns selection.

## Mode selection

| Mode | Select when | Minimum evidence | Primary output |
|---|---|---|---|
| `single-skill-benchmark` | one existing target needs maturity scoring | target package/content | scorecard + gates + verdict |
| `comparison-benchmark` | baseline/candidate or parent/candidate deltas are requested | separately frozen targets + same evaluator/scenario identities | comparable deltas + capability findings |
| `report-validation` | a benchmark report already exists | report file/text | validation findings |
| `behavioral-evidence-benchmark` | executed/supplied scenario results must be interpreted | schema-valid result evidence | metrics + provenance/claim limits |
| `portability-benchmark` | multi-host support is claimed/requested | target + host profiles | portable-core/adapter findings |
| `template-only` | no inspectable target is available | explicit missing-input state | report skeleton only; no score/readiness claim |

## Quick start

1. Resolve exactly one benchmark target or report, select the mode, and record requested hosts/output destination.
2. For filesystem targets, read `SKILL.md` first, keep outputs outside the target, and run normative Agent Skills conformance before maturity scoring.
3. Freeze target bytes and evaluator identity before strict comparison or measured claims; benchmark the frozen snapshot, not a silently changing live tree.
4. Score static maturity with [`references/benchmark-rubric.md`](references/benchmark-rubric.md); do not treat host adapters or optional resource count as automatic quality points.
5. Validate behavioral result envelopes before computing metrics; prefer v3 repeated trials for stochastic/model-agent claims and validate benchmark health before strong behavioral promotion claims.
6. Compare only like-for-like evidence. Changed evaluator/scenario/runtime/host identities make strict deltas `not comparable` unless the benchmark contract explicitly controls the difference.
7. Validate the generated report, reverify source identity, freeze accepted evidence after the final pass, and deliver report/receipt atomically when writing files.

## Critical evidence and decision rules

- Evidence layers stay distinct: `static`, `behavioral`, `runtime`, `qualitative`, `planned`, and `blocked`.
- Never turn planned, missing, stale, malformed, contaminated, or unvalidated evidence into measured claims.
- A static 0-100 score is a maturity score, not behavioral capability proof and not normative Agent Skills conformance.
- Hard gates run before score-based comparison; a better scalar score never overrides a blocker regression.
- Existing-skill regression claims keep the immutable prior version as `baseline`; `without-skill` answers incremental value and never replaces that baseline.
- Direct `parent` is for local transformation attribution; keep candidate-vs-parent separate from candidate-vs-baseline.
- Hidden/blind evaluation requires evaluator-only assets to remain candidate-invisible; byte identity alone does not prove non-contamination.
- Do not invent activation precision/recall, robustness, conformance, coverage, quality, rework, cost, or portability/runtime results.
- If several candidates are non-dominated and no frozen weighting policy exists, report the frontier instead of manufacturing a winner.
- Portability claims concern the semantic core; host adapters are optional and must not add score merely by existing.

## Required inputs and protected evidence

Required: target content/path/source (or report text for `report-validation`), benchmark mode, and report destination or inline-report choice. Optional: baseline/parent/control arms, scenario results, prior reports, review notes, issue links, requested hosts, and staged-evaluation metadata.

Protect target files, fixtures, expected outputs, secrets, credentials, frozen evaluator/scenario inputs, generated baseline evidence, and read-only paths. Never alter them to make a benchmark pass. If no inspectable target exists, use `template-only` and return missing inputs without a score or readiness verdict.

## Direct resource map

- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): score dimensions, blocker gates, verdict thresholds, evidence-identity rules.
- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): filesystem sequence, evidence hierarchy, comparison rules, output ownership, final response.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): immutable snapshots, evaluator identity, alias safety, atomic delivery, recovery receipts.
- [`references/test-scenarios.md`](references/test-scenarios.md) and [`references/experimental-evidence.md`](references/experimental-evidence.md): v2/v3 result contracts, repeated trials, runtime identity, uncertainty, grader/length controls.
- [`references/benchmark-health.md`](references/benchmark-health.md) and [`references/skill-coverage.md`](references/skill-coverage.md): suite-health gate and optional constraint-level behavioral coverage.
- [`references/control-and-capability-delta.md`](references/control-and-capability-delta.md): baseline/parent/no-skill/length-control roles, visibility, provenance, capability delta.
- [`references/evaluation-ladder-and-parent-comparison.md`](references/evaluation-ladder-and-parent-comparison.md) and [`references/multi-candidate-evaluation.md`](references/multi-candidate-evaluation.md): staged L0-L5 evidence, parent attribution, multi-candidate comparability without survivor selection.
- [`references/host-portability.md`](references/host-portability.md): host-neutral semantic core, adapters, capability detection, portability limits.
- [`references/report-template.md`](references/report-template.md): required report sections and ordering.

## Host portability

Use the open Agent Skills package as the semantic core. Do not make benchmark behavior depend on ChatGPT-, Codex-, Claude-, Copilot-, Cursor-, or vendor-private tool names. `agents/openai.yaml` is an optional OpenAI adapter and must not add score merely by existing.

When portability matters, read [`references/host-portability.md`](references/host-portability.md). Resolve capabilities before execution rather than branching only on product name:

1. filesystem read;
2. writable work/output location outside protected target evidence;
3. Python 3.10+ or equivalent command execution;
4. optional independent scenario/evaluator execution;
5. artifact delivery.

Denote the resolved Python launcher/execution method as `<PYTHON>`; do not assume `python3`, Bash, POSIX utilities, or a specific sandbox path.

## Detailed resource catalog

Load only resources required by the selected mode/claim:
- [`references/benchmark-workflow.md`](references/benchmark-workflow.md): portable commands, evidence hierarchy, comparison, paths, final response.
- [`references/benchmark-rubric.md`](references/benchmark-rubric.md): dimensions, weights, gates, verdict rules.
- [`references/test-scenarios.md`](references/test-scenarios.md): v2 compatibility plus preferred v3 repeated-trial scenario evidence.
- [`references/experimental-evidence.md`](references/experimental-evidence.md): uncertainty-aware comparisons, runtime identity, efficiency, grader calibration, and length-control semantics.
- [`references/benchmark-health.md`](references/benchmark-health.md): benchmark task/grader/isolation/contamination/saturation health gate.
- [`references/skill-coverage.md`](references/skill-coverage.md): optional constraint-level skill behavior coverage.
- [`references/report-template.md`](references/report-template.md): required report sections/order.
- [`references/host-portability.md`](references/host-portability.md): portable core, host profiles, capability rules.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): source snapshots, evaluator identity, alias safety, recovery, receipts.
- [`references/control-and-capability-delta.md`](references/control-and-capability-delta.md): no-skill control-arm rules, hidden-evaluator visibility, trace provenance, and deterministic capability-delta interpretation.
- [`references/evaluation-ladder-and-parent-comparison.md`](references/evaluation-ladder-and-parent-comparison.md): L0-L5 staged evaluation, direct-parent attribution, hard-gate-first comparison, and non-dominated multi-metric reporting.
- [`references/multi-candidate-evaluation.md`](references/multi-candidate-evaluation.md): identity/comparability contract for evaluating several search candidates without taking ownership of survivor selection.
- [`assets/templates/benchmark-report.md.template`](assets/templates/benchmark-report.md.template): manual report skeleton.
- [`assets/templates/scenario-results.json.template`](assets/templates/scenario-results.json.template): v2 compatibility results skeleton.
- [`assets/templates/scenario-results-v3.json.template`](assets/templates/scenario-results-v3.json.template): preferred repeated-trial behavioral results skeleton.
- [`assets/templates/benchmark-health.json.template`](assets/templates/benchmark-health.json.template): benchmark-health evidence skeleton.
- [`assets/templates/skill-coverage.json.template`](assets/templates/skill-coverage.json.template): constraint-coverage evidence skeleton.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation/non-activation/ambiguous/edge/regression/adversarial coverage.
- [`examples/activation-scenarios.json`](examples/activation-scenarios.json): compact activation calibration examples.
- [`scripts/snapshot_target.py`](scripts/snapshot_target.py): capture/verify exact target bytes.
- [`scripts/benchmark_identity.py`](scripts/benchmark_identity.py): compute frozen evaluator identity.
- [`scripts/generate_benchmark_report.py`](scripts/generate_benchmark_report.py): portable deterministic report generator.
- [`scripts/validate_benchmark_report.py`](scripts/validate_benchmark_report.py): report/evidence validator.
- [`scripts/validate_scenario_results.py`](scripts/validate_scenario_results.py): v2/v3 scenario evidence validator.
- [`scripts/validate_agent_skills_spec.py`](scripts/validate_agent_skills_spec.py): normative Agent Skills conformance gate.
- [`scripts/validate_benchmark_health.py`](scripts/validate_benchmark_health.py): independent benchmark-health validator.
- [`scripts/validate_skill_coverage.py`](scripts/validate_skill_coverage.py): constraint coverage/adherence validator.
- [`scripts/compare_benchmark_arms.py`](scripts/compare_benchmark_arms.py): compare candidate against baseline/parent/without-skill/optional length-control with v3 uncertainty and separate efficiency deltas.
- [`scripts/validate_portability.py`](scripts/validate_portability.py): structural portability validator.
- [`scripts/package_skill.py`](scripts/package_skill.py): deterministic portable package builder with atomic receipt.


- `scripts/validate_candidate_set.py`: validates multi-candidate evidence; evolutionary-search contract v4 additionally freezes scoring-policy identity, candidate/parent identities, evaluation level, requires a non-empty comparable metric set, and validates metric uncertainty.
- `contracts/integration-manifest.json`: declares the benchmark multi-candidate evidence contract for cross-skill impact analysis.

## Workflow

### 1. Establish target and capabilities

1. Resolve exactly one target root containing `SKILL.md` when filesystem content exists.
2. Read target `SKILL.md` first; inventory relevant references/scripts/assets/examples/evals/adapters.
3. Select mode, requested hosts, `<PYTHON>`, writable work dir, protected paths, and behavioral evidence policy.
4. For filesystem targets, run the normative Agent Skills conformance gate before maturity scoring.
5. Keep benchmark outputs outside the target package.

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

For new stochastic/model-agent runs, prefer v3 repeated-trial evidence. Keep v2 readable for compatibility but do not use a one-observation v2 delta as a strong stochastic improvement claim. When a strong behavioral verdict depends on the suite, validate benchmark health first; a health `fail` blocks the claim and `review` limits it. Optional skill-coverage evidence can show which material constraints were actually exercised.

Validate scenario evidence before metrics:

```text
<PYTHON> scripts/validate_scenario_results.py --results <RESULTS_JSON> --json-output <WORK>/scenario-validation.json
```

Accept the versioned v2/v3 envelopes in [`references/test-scenarios.md`](references/test-scenarios.md). Prefer v3 for repeated stochastic trials; record runtime identity, suite role/distribution, grader calibration when applicable, trace identity when available, and evaluator visibility/leakage status for hidden graders/holdouts. Reject top-level arrays and unversioned result shapes.

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
6. optionally add a `length-control` arm when context-length/distraction is a material confound; keep it diagnostic and separate;
7. keep the prior-version baseline as the primary regression baseline for existing-skill updates;
8. for v3, require the same runtime-profile identity and use uncertainty-aware `claim_classification`; keep efficiency deltas separate from capability;
9. reject blind/hidden-evaluator claims when candidate execution could read evaluator-only assets;
10. if evaluator/scenario/runtime/host configuration identities differ materially, show standalone results and label delta `not comparable`.

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
- scenario coverage across activation/non-activation/ambiguous/edge cases plus suite role/distribution semantics;
- benchmark-health status when behavioral promotion claims rely on the suite;
- repeated-trial uncertainty/claim classification for v3 stochastic comparisons;
- efficiency metrics separately from capability metrics when supplied;
- skill behavior constraint coverage when supplied;
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
- strict comparison lacks stable baseline/candidate/evaluator/scenario identity, or v3 runtime identity;
- a strong behavioral claim relies on a benchmark-health `fail` state;
- a hidden/blind evaluator claim is requested but evaluator-only assets were visible to the evaluated candidate or leakage status is unknown;
- report would cite uninspected files;
- output aliases target/protected evidence/receipt;
- scenario evidence is malformed or identity-conflicted;
- required portability claim depends on host-private core behavior;
- generated report validation fails and cannot be corrected from available evidence.

## Validation and finalization

Before completion confirm: Agent Skills conformance for filesystem targets; stable target identity or explicit `live-unfrozen` limitation; evaluator identity for strict comparisons; required report sections; visible failed/review gates; metric-status distinctions; local references resolve; useful resources are not penalized merely for existing; requested-host portability is separated from runtime support; report validator passes when runnable; scenario validator passes before behavioral metrics are used; arm comparison validation passes before capability-delta claims; hidden-evaluator visibility/leakage evidence supports any blind-evaluation claim; accepted evidence is frozen after the final pass; atomic delivery/last-known-good recovery gates passed when files were written; no target/evaluator/report/scenario edit occurred after frozen evidence was accepted.

Report generated paths/content, commands, score, gate status, source/evaluator identities, behavioral evidence status, portability status, missing evidence, and residual risks. If an applicable hard gate did not run or failed, do not claim readiness/completion beyond the evidence actually established.
