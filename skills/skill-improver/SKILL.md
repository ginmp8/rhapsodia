---
name: skill-improver
description: use for existing agent skills-compatible packages across chatgpt/codex, claude, github copilot, cursor, or similar hosts when asked to audit, review-fix-review, improve, harden, self-improve, validate, benchmark, package, install, materialize evolution/search candidates, or run bounded hypothesis-driven experiments. preserve immutable baselines, freeze evaluators, use deterministic severity/lifecycle rules, reject regressions through structural gates, preserve rollback evidence, and freeze validated candidates. do not use for new skills, ordinary repository refactors, evaluator-fixture edits, or unbounded automation without an explicit disposable sandbox and budget.
---

# Skill Improver

## Mission and boundaries

Improve one existing skill through bounded, reproducible experiments. Preserve an immutable baseline, freeze deciding evidence before mutation, test an evidence-backed hypothesis, compare with the same evaluator, apply an independent structural gate, retain rejected evidence, and freeze only an accepted candidate. Never improve a score by weakening activation, semantics, safety, compatibility, validation, evidence, or protected fixtures.

Use only for existing skill packages: audit/benchmark, bounded patching or automation, reproducibility hardening, self-improvement, validation, installation, packaging, and caller-routed evolution/search candidate materialization. Do not own net-new skill creation, generic repositories/application code, broad specialist orchestration, evaluator-fixture edits, secrets, generated evidence, or unbounded automation.

Reproducibility means repeated runs on the same supported inputs/environment satisfy the same semantic contract and gates; subjective/model judgment need not produce identical prose. Keep evidence layers distinct: **structural** (package/schema/hash), **behavioral** (executed scenarios), **runtime** (actual tool/app execution), and **perceptual** (independent subjective review). Never promote a weaker layer into a stronger claim.

## Required inputs and defaults

Resolve before mutation:

- `TARGET_SKILL_PATH`: exactly one existing skill root or extracted archive.
- mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
- runtime capabilities: read/write filesystem, Python 3.10+, command execution, optional network/research, independent evaluation, artifact delivery.
- evaluator contract: command/benchmark, selected optimization metric/delta, hard gates, frozen/blocked paths, evaluation partitions, runtime identity, and a non-saturated auxiliary metric when needed. Predeclare `no-skill`, `parent`, and `candidate` for marginal-value claims.
- hypothesis source: user/backlog/`skill-hypothesis-discovery`/fallback; when supplied, preserve change intent, transformation/capability ids, parent identity, and prior evidence.
- material source evidence, mutation scope, finite budget, safety posture, change-gate policy, and delivery paths.

Defaults: snapshot before mutation; one bounded manual patch or at most three automated iterations; `--min-delta 1.0` applies only to the selected optimization metric and never overrides hard gates; mutate target folder only; protect fixtures/expected outputs/evaluators/reports/evidence/packages/caches/`.git`/credentials/secrets; snapshot material source evidence; require the runner change gate when available; freeze the final pass. Strong stochastic claims require repeated trials; promotion-sensitive claims require a controller-only holdout.

## Modes

| Mode | Contract |
|---|---|
| `benchmark-only` | frozen evaluation/report only; no mutation |
| `manual-patch` | baseline -> one bounded hypothesis -> minimal candidate -> evaluate/gate -> accept/reject -> freeze |
| `automated-loop` | require clean working copy, frozen evaluator identity, hypothesis source, finite budget, rollback/blocked paths, stop condition, supported agent adapter |
| `package-install` | validate/freeze first; package/install atomically with hashes/receipt |
| `self-improvement` | immutable external controller + baseline, isolated candidate, recursion depth 1 by default, external promotion gate, last-known-good preservation |

## Progressive resources

Load only what the active branch needs:

- evaluation and mutation: [evaluation contract](references/evaluation-contract.md), [transformation/ablation](references/transformation-records-and-ablation.md), [severity lifecycle](references/severity-lifecycle.md), [reproducibility controls](references/reproducibility-controls.md), [self-improvement protocol](references/self-improvement-protocol.md).
- evolution/search: [candidate execution](references/evolution-candidate-execution.md), `scripts/validate_candidate_request.py`, `scripts/validate_generation_receipt.py`, and `contracts/integration-manifest.json`.
- portability/runtime: [host portability](references/host-portability.md), [execution runbook](references/execution-runbook.md), [environment provenance](references/environment-provenance.md), [stochastic evaluation](references/stochastic-evaluation.md), [autoresearch adaptation](references/autoresearch-adaptation.md), and `scripts/validate_execution_evidence.py` when runtime comparability or repeated-trial claims are material.
- evaluation design: [benchmark integration](references/benchmark-integration.md), [hypothesis catalog](references/hypothesis-catalog.md), [harness design](references/harness-design.md), `skill-hypothesis-discovery`, canonical planned scenarios in `evals/activation-scenarios.json`, [evaluation plan template](assets/templates/evaluation-plan.json.template) with `scripts/validate_evaluation_plan.py`, and [paired trials template](assets/templates/paired-trials.json.template) with `scripts/summarize_paired_trials.py`.
- state/delivery: `scripts/evidence_snapshot.py`, `scripts/skill_improver_status.py`, `scripts/skill_improver_loop.py`, `scripts/static_skill_score.py`, `scripts/validate_self_improvement_receipt.py`, `scripts/validate_transformation_record.py`, `scripts/validate_skill_improver_package.py`, `scripts/package_skill.py`, [report contract](references/report-template.md), [generation receipt template](assets/templates/generation-receipt.json.template), [transformation template](assets/templates/transformation-record.json.template), [improvement report template](assets/templates/improvement-run-report.md.template), and [patch decision template](assets/templates/patch-decision-record.md.template).

The command adapter is the portable runner default; optional Codex support is an adapter, never part of the semantic core. Static scores are regression gates when saturated, not improvement evidence.

## Workflow

1. **Establish** one target, objective, runtime profile, writable/protected scope, finite budget and delivery expectation. Snapshot the baseline. For self-improvement also freeze controller, generation, last-known-good and isolated candidate identities; never edit the active controller.
2. **Freeze deciding evidence**: evaluator/scenario/expected-output/scoring/blocked-path identity plus material source bytes. Separate mutator-visible diagnostics, read-only regression evidence, and controller-only promotion holdout; freeze an evaluation plan for tri-arm, stochastic, runtime-identity, or capability-delta claims. Evidence drift or holdout contamination invalidates the experiment unless explicitly re-baselined.
3. **Measure and diagnose**: record baseline metrics/gates/identities and unresolved risk. For marginal value measure `no-skill`, `parent`, and `candidate` under comparable runtime identity; repeat stochastic trials with a declared reliability metric. Treat saturated metrics as gates, add an active auxiliary metric, and diagnose from captured failures/traces rather than suspicion.
4. **Select one bounded hypothesis or inseparable batch**: record change intent (`repair|optimization|simplification|experiment`), mechanism/evidence, transformation/capability ids, parent, expected effect, evaluator/acceptance rule, rollback, and mutation owner. `simplification` must preserve capability/quality gates while reducing context cost, brittleness, or obsolete scaffolding.
5. **Materialize the smallest candidate**. Caller-routed search requests must satisfy [candidate execution](references/evolution-candidate-execution.md); otherwise follow [transformation records](references/transformation-records-and-ablation.md). Preserve parent/transformation provenance and move only genuinely mechanical variance into scripts/schemas/validators.
6. **Evaluate/repair** with the frozen evaluator and protected/source identities. Keep hard gates separate from optimization dimensions; scalar gains cannot override activation, safety, compatibility, evaluator integrity, or unauthorized capability delta. When applicable compute parent delta and no-skill Skill Lift, record trials/runtime/contamination/capability evidence, and run holdout only controller-side. Repair one diagnosed cause, rerun the narrowest failed gate, then adjacent gates; stop after two non-improving repairs without new evidence.
7. **Decide**: reject identity/protected-path drift, holdout contamination, material un-rebaselined runtime drift, failed hard gates/thresholds, blocking regression, weakened semantics/safety, or unauthorized authority expansion. Preserve rejection evidence/last-good state; a self-improving candidate cannot promote itself.
8. **Freeze and deliver** the exact passing candidate. Any later edit reopens affected validation. Canonicalize output/receipt paths, reject aliases with protected inputs, stage/validate/hash before commit, preserve recovery artifacts on failure, and emit a receipt tied to committed bytes.
9. **Report truthfully**: identify parent/transformation/candidate/evaluator/scenario identities, baseline/final metrics, commands and outcomes, accepted/rejected hypotheses, gate decision, protected paths, termination/rollback, evidence layers, residual risk, and package/receipt hashes only when actually validated.

## Output contract

For substantive mutating runs report target/mode/objective and baseline identity; frozen evaluator/source identities; selected/accepted/rejected hypotheses with transformation/capability refs; changed files; exact validations; change-gate decision; protected paths and rollback/recovery; final candidate/termination/evidence-layer limits; residual risk; and validated package/receipt hashes. When applicable also report arms/partitions, parent delta and no-skill Skill Lift, repeated-trial uncertainty, runtime comparability, contamination, hard-gate vs optimization results, and capability/authority delta. Search candidates additionally report request/parent/donor/operator/transformation/capability identities and generation-receipt v3; self-improvement also reports controller/generation/last-known-good and external promotion status.

## Evolution/search contract

When a caller supplies an evolution request, preserve its v2 identity (`request_signature`, base/donor parents, operator, transformations, expected capability effects), validate before mutation, and return a validated **generation-receipt v3** for the materialized candidate. `skill-improver` owns candidate materialization only; population/search state, selection and promotion remain external. Current peer contracts in `contracts/integration-manifest.json` are public compatibility surfaces.

## Stop conditions

Stop/revert/return a bounded partial result when target or baseline identity is unsafe/ambiguous; required source truth or frozen evaluator is unavailable; protected evidence changes; mutation needs blocked fixtures/secrets/unrelated paths; a required runtime/gate is unavailable; the same objective repair fails twice without new evidence; output paths alias protected inputs; validation/package/source verification fails; or passing requires weakening a hard gate. Report `blocked`/`not-run` rather than inventing success.

## Final checklist

Before success, verify frozen evaluators covered comparable arms; no-skill control exists for marginal-value claims; holdout stayed controller-only with explicit contamination state; stochastic claims have repeated trials; runtime identity is comparable or re-baselined; capability delta adds no unauthorized authority; source snapshots still match; auxiliary evidence supports saturated metrics; target tests/validators and independent change gate pass; blocked paths remain unchanged; modified scripts ran or were syntax-checked; no post-freeze edits occurred; output aliases are rejected; artifact/receipt hashes match exact bytes; and scenario rates come only from captured executions. For self-improvement also validate controller/promotion separation and its receipt.

## Orchestration boundary

Own bounded improvement experiments and self-improvement generation state only. Consume directly related evaluator, hypothesis, change-gate and caller-supplied review evidence through declared contracts; do not discover, sequence, or absorb a broad specialist catalog. The caller/orchestrator retains global routing and final promotion authority.
