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
- evaluator contract: command/benchmark, direction, minimum delta, required gates, frozen/blocked paths, and a non-saturated auxiliary metric when needed.
- hypothesis source: user/backlog/`skill-hypothesis-discovery`/fallback; when supplied, preserve change intent, transformation/capability ids, parent identity, and prior evidence.
- material source evidence, mutation scope, finite budget, safety posture, change-gate policy, and delivery paths.

Defaults: snapshot before mutation; one bounded manual patch or at most three automated iterations; `--min-delta 1.0`; mutate target folder only; protect fixtures/expected outputs/evaluators/reports/evidence/packages/caches/`.git`/credentials/secrets; source-snapshot material evidence; require the runner change gate when a gate command exists, otherwise advisory; freeze the final pass before delivery.

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
- portability/runtime: [host portability](references/host-portability.md), [execution runbook](references/execution-runbook.md), [autoresearch adaptation](references/autoresearch-adaptation.md).
- evaluation design: [benchmark integration](references/benchmark-integration.md), [hypothesis catalog](references/hypothesis-catalog.md), [harness design](references/harness-design.md), `skill-hypothesis-discovery`, and canonical planned scenarios in `evals/activation-scenarios.json`.
- state/delivery: `scripts/evidence_snapshot.py`, `scripts/skill_improver_status.py`, `scripts/skill_improver_loop.py`, `scripts/static_skill_score.py`, `scripts/validate_self_improvement_receipt.py`, `scripts/validate_transformation_record.py`, `scripts/validate_skill_improver_package.py`, `scripts/package_skill.py`, [report contract](references/report-template.md), [generation receipt template](assets/templates/generation-receipt.json.template), [transformation template](assets/templates/transformation-record.json.template), [improvement report template](assets/templates/improvement-run-report.md.template), and [patch decision template](assets/templates/patch-decision-record.md.template).

The command adapter is the portable runner default; optional Codex support is an adapter, never part of the semantic core. Static scores are regression gates when saturated, not improvement evidence.

## Workflow

1. **Establish** one target, objective, runtime profile, writable/protected scope, finite budget and delivery expectation. Snapshot the baseline. For self-improvement also freeze controller, generation, last-known-good and isolated candidate identities; never edit the active controller.
2. **Freeze deciding evidence**: evaluator scripts/scenarios/expected outputs/scoring config/blocked paths plus any material external source bytes. If deciding evidence changes, invalidate or explicitly re-baseline the experiment.
3. **Measure and diagnose**: record baseline metrics/gates/identities and unresolved risk. Treat saturated metrics as gates and add an active auxiliary metric. Use deterministic severity/tie-break rules; do not patch unverified suspicions.
4. **Select one bounded hypothesis or inseparable batch**: record change intent (`repair|optimization|experiment`), mechanism/evidence, transformation and capability ids, parent, expected effect, evaluator/acceptance rule, rollback, and mutation owner.
5. **Materialize the smallest candidate**. Caller-routed search requests must satisfy [candidate execution](references/evolution-candidate-execution.md); otherwise follow [transformation records](references/transformation-records-and-ablation.md). Preserve parent/transformation provenance and move only genuinely mechanical variance into scripts/schemas/validators.
6. **Evaluate/repair** with the frozen evaluator and protected/source identities. Repair one diagnosed cause, rerun the narrowest failed gate, then adjacent gates. Stop a branch after two consecutive non-improving repairs on the same objective error set unless new evidence appears.
7. **Decide**: reject on identity/protected-path drift, failed required gates, missed acceptance threshold, blocking structural regression, or weakened semantics/safety. Keep accepted changes only and preserve rejection evidence/last-good state. A self-improving candidate cannot authorize its own promotion.
8. **Freeze and deliver** the exact passing candidate. Any later edit reopens affected validation. Canonicalize output/receipt paths, reject aliases with protected inputs, stage/validate/hash before commit, preserve recovery artifacts on failure, and emit a receipt tied to committed bytes.
9. **Report truthfully**: identify parent/transformation/candidate/evaluator/scenario identities, baseline/final metrics, commands and outcomes, accepted/rejected hypotheses, gate decision, protected paths, termination/rollback, evidence layers, residual risk, and package/receipt hashes only when actually validated.

## Output contract

For substantive mutating runs report target/mode/objective and baseline identity; frozen evaluator/source identities and baseline/final metrics; selected/accepted/rejected hypotheses with transformation/capability refs; changed files; exact validation commands and outcomes; change-gate decision; protected paths and rollback/recovery; final frozen candidate identity; termination state; evidence-layer limits; residual risk; and package/install/receipt hashes only when produced and validated. Search candidates additionally report request signature, parent/donor ids, operator, transformations, expected capability effects, and validated generation-receipt v3. Self-improvement additionally reports controller/generation/last-known-good identities and external promotion status.

## Evolution/search contract

When a caller supplies an evolution request, preserve its v2 identity (`request_signature`, base/donor parents, operator, transformations, expected capability effects), validate before mutation, and return a validated **generation-receipt v3** for the materialized candidate. `skill-improver` owns candidate materialization only; population/search state, selection and promotion remain external. Current peer contracts in `contracts/integration-manifest.json` are public compatibility surfaces.

## Stop conditions

Stop/revert/return a bounded partial result when target or baseline identity is unsafe/ambiguous; required source truth or frozen evaluator is unavailable; protected evidence changes; mutation needs blocked fixtures/secrets/unrelated paths; a required runtime/gate is unavailable; the same objective repair fails twice without new evidence; output paths alias protected inputs; validation/package/source verification fails; or passing requires weakening a hard gate. Report `blocked`/`not-run` rather than inventing success.

## Final checklist

Before success, verify the same frozen evaluator covered baseline and candidate; source snapshots still match or were deliberately re-baselined; saturated metrics used auxiliary evidence for improvement claims; target validators/tests and independent change gate passed; blocked paths stayed unchanged; modified scripts ran or were syntax-checked; final candidate was untouched after freeze; output aliases were rejected; committed artifact/receipt hashes match exact bytes; package scope is exact; and scenario rates are claimed only from captured executions. For self-improvement, additionally validate external controller/promotion separation and the self-improvement receipt.

## Orchestration boundary

Own bounded improvement experiments and self-improvement generation state only. Consume directly related evaluator, hypothesis, change-gate and caller-supplied review evidence through declared contracts; do not discover, sequence, or absorb a broad specialist catalog. The caller/orchestrator retains global routing and final promotion authority.
