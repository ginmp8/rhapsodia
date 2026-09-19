---
name: skill-improver
description: use for existing agent skills-compatible packages across chatgpt/codex, claude, github copilot, cursor, or similar hosts when asked to audit, review-fix-review, improve, harden, self-improve, validate, benchmark, package, install, migrate legacy skill-improvement workflows, or run bounded hypothesis-driven experiments. preserve immutable baselines, freeze evaluators, use deterministic severity/lifecycle rules, reject regressions through structural gates, preserve rollback evidence, and freeze validated candidates. do not use for new skills, ordinary repository refactors, evaluator-fixture edits, or unbounded automation without an explicit disposable sandbox and budget.
---

# Skill Improver

## Purpose

Improve an existing skill through controlled, reproducible experiments. Preserve a baseline, freeze the evaluator, snapshot material external evidence when it affects the decision, measure the baseline, test one bounded hypothesis, re-run the same evaluator, apply an independent structural change gate, and accept only when the predeclared rule passes without weakening semantics, safety, compatibility, validation, or evidence. Freeze the accepted candidate before delivery; any later edit invalidates the affected evidence and requires revalidation.

Treat `SKILL.md` as the compact control plane. Load branch-specific references only when needed.

## Scope

Use for existing skill packages when the task is benchmarking, auditing, scoring, manual improvement, bounded autonomous improvement, reproducibility hardening, self-improvement with safeguards, validation, installation, or packaging.

Do not use for new skill creation, generic repository refactors, ordinary application-code work, edits to evaluator fixtures or expected outputs, generated evidence, secrets, unrelated paths, or unbounded/yolo automation outside an acknowledged disposable sandbox.

## Reproducibility boundary

The target may contain subjective or model-judgment behavior. Reproducibility means repeated runs against the same supported inputs and environment satisfy the same semantic contract and gates; it does not require byte-identical prose unless the target domain can guarantee that.

Use these evidence labels separately:
- **structural**: package shape, links, schemas, validators, frozen hashes;
- **behavioral**: executed scenarios/evaluators against the target behavior;
- **runtime**: actual tool/browser/application execution;
- **perceptual**: independent human or image-capable review for subjective quality.

Do not claim a stronger layer from a weaker one.

## Inputs and default policy

Resolve before mutation:
1. `TARGET_SKILL_PATH`: folder or extracted archive containing exactly one target `SKILL.md`.
2. Mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
3. Runtime capability profile: filesystem read/write, Python 3.10+, command execution, network/research when freshness matters, independent evaluator/subagent support, artifact delivery.
4. Evaluator contract: command or benchmark, score direction, minimum delta, required gates, locks, blocked paths, auxiliary metric when the primary metric is saturated.
5. Hypothesis source: user-supplied hypothesis, supplied backlog, `skill-hypothesis-discovery`, or built-in catalog fallback.
6. Material source evidence: external files/repository content whose exact bytes affect the hypothesis or acceptance decision.
7. Budget and safety posture: iteration/time budget, sandbox/manual-review posture, allowed mutation scope.
8. Structural change-gate policy: `disabled`, `advisory`, or `required`.
9. Final artifact and delivery paths: report, patched folder, installed folder, package zip, optional receipt.

Defaults: preserve a baseline before mutation; one bounded manual patch or max three automated iterations; `--min-delta 1.0`; target-folder-only mutation; evaluator files, fixtures, reports, generated evidence, packages, caches, `.git`, credentials, and secrets blocked; snapshot material external source bytes before analysis; runner change-gate policy resolves to `required` when a gate command is supplied and otherwise `advisory`; manual patches may explicitly use advisory; manual review unless a stronger sandbox exists; final candidate frozen after pass; package/output paths preflighted before writes.

## Mode selection

- `benchmark-only`: run the frozen evaluator and report; do not mutate.
- `manual-patch`: baseline -> freeze -> select one bounded hypothesis -> minimal patch -> evaluate -> change gate -> accept/reject -> freeze final candidate.
- `automated-loop`: require clean working copy, evaluator hash, hypothesis source, budget, rollback log, blocked paths, stop condition, and an agent adapter supported by the current host.
- `package-install`: validate a frozen candidate, preflight destinations, then atomically package/install with hash/receipt evidence.
- `self-improvement`: follow `references/self-improvement-protocol.md`; freeze an immutable controller and baseline, mutate only an isolated candidate, default self-recursion depth to 1, preserve last-known-good, and require final validation/promotion outside the candidate mutation surface.

## Resource loading

Load only what the active branch needs:
- `references/evaluation-contract.md`: evaluator schema, freeze rules, acceptance, metric gates, hypothesis policy, structural change-gate policy.
- `references/severity-lifecycle.md`: stable severity taxonomy, deterministic triage, iteration state, completion/cancellation semantics, and max-iteration rules.
- `references/legacy-migration.md`: migration map from the deprecated `skill-improvement` workflow and compatibility commitments.
- `references/reproducibility-controls.md`: source snapshots, repair rules, freeze-after-pass, canonical path preflight, recovery-aware delivery, durable receipts, evidence layers.
- `references/self-improvement-protocol.md`: controller/baseline/candidate separation, generation identity, recursion limit, promotion, last-known-good, and self-improvement receipt rules.
- `references/host-portability.md`: portable Agent Skills core, capability-first execution, Python/CLI portability, optional host adapters.
- `references/benchmark-integration.md`: benchmark integration and saturated-score handling.
- `references/hypothesis-catalog.md`: fallback hypotheses and expected evidence.
- `skill-hypothesis-discovery` or compatible backlog JSON: use when no bounded hypothesis is supplied, metrics are saturated, or the next candidate is unclear.
- `references/autoresearch-adaptation.md`: bounded autonomous-loop mechanics.
- `references/execution-runbook.md`: CLI modes, agent adapters, packaging, rollback, source snapshots.
- `references/harness-design.md`: scenario metrics and auxiliary evidence.
- `references/report-template.md`: final report contract.
- `evals/skill-improver-scenarios.json`: planned activation/negative/ambiguous/edge/regression suite; treat as frozen during candidate optimization unless benchmark design is the task.
- `scripts/evidence_snapshot.py`: deterministic capture/verify/hash helper for material source evidence and candidate identity.
- `scripts/skill_improver_status.py`: read-only status derivation from canonical `.skill-improver/` run evidence; it does not maintain a parallel session store.
- `scripts/skill_improver_loop.py`: optional autonomous runner; its Codex adapter is not the portable semantic core.
- `scripts/static_skill_score.py`: deterministic starter evaluator; saturated scores are gates only.
- `scripts/validate_self_improvement_receipt.py`: deterministic gate for controller/candidate separation and promotion-receipt integrity in self-improvement mode.
- `skill-change-gate` or compatible command: independent structural regression gate.
- `scripts/validate_skill_improver_package.py` and `scripts/package_skill.py`: package validation and recovery-aware packaging.
- `assets/templates/improvement-run-report.md.template` and `assets/templates/patch-decision-record.md.template`: templates consumed by the runner.

## Workflow

1. **Identify and snapshot**: resolve one target root; record target identity, requested objective, runtime capabilities, writable scope, protected paths, and final delivery expectation. Preserve an immutable baseline before edits. In `self-improvement`, also freeze `controller_identity`, `generation_id`, `last_known_good_identity`, isolated candidate path, and `max_self_recursion_depth` before mutation; never edit the active controller in place.
2. **Freeze evaluation**: define evaluator/metric contract; hash evaluator scripts, scenarios, expected outputs, scoring config, benchmark inputs, and blocked paths. A frozen evaluator must not change to make a candidate pass.
3. **Snapshot material sources**: when external files or repository evidence affect the patch or acceptance decision, capture their exact bytes before analysis and verify them again before final acceptance. If they changed, explicitly re-baseline or invalidate the comparison.
4. **Measure baseline**: record score, status, gates, evaluator hash, source snapshot identity, command, report path, and unresolved risks. If the primary metric is saturated, keep it as a gate and define a non-saturated auxiliary metric before claiming improvement.
5. **Diagnose and triage**: use `references/severity-lifecycle.md` to classify findings as `critical`, `major`, `minor`, or `needs-verification`, apply its tie-breakers, and process blocking severity first. Prefer observable failure signals over taste; never auto-fix an unverified suspicion.
6. **Discover/select one hypothesis**: state mechanism, evidence signal, files, expected effect, validation method, accept/reject rule, rollback plan, and expected reproducibility control. Use evidence-backed discovery before built-in fallback when the next candidate is unclear.
7. **Apply the smallest coherent candidate**: mutate only allowed paths. Move mechanical/repetitive rules into scripts/schemas/validators when that reduces variance; keep model judgment only where it is genuinely needed. Never weaken evaluator, safety, activation, output, compatibility, or package gates.
8. **Repair by diagnosis**: run the narrowest failing validator, identify one causal subject, apply the smallest supported fix, rerun the same gate, then adjacent gates. Stop a branch after two consecutive non-improving rounds on the same objective error set unless new evidence appears.
9. **Evaluate and change-gate**: re-run the same frozen evaluator and verify protected/source identities. Reject if hashes changed, blocked paths changed, evaluator gates fail, the metric misses the threshold, or the structural gate finds a blocking regression.
10. **Accept, rollback, or stop**: keep accepted changes only. Revert rejected candidates while preserving the last accepted state and rejection evidence. In `self-improvement`, the candidate cannot authorize its own promotion; require the frozen external/change-gate surface, emit and validate the self-improvement receipt, and promote only the exact frozen candidate. Use the canonical termination states in `references/severity-lifecycle.md`; honor explicit stop files between iterations; cancellation must not fabricate completion.
11. **Freeze final candidate**: once final validation passes, compute/record the exact candidate identity and make no unvalidated cleanup edits. Any later edit requires revalidation from the affected gate.
12. **Deliver atomically**: preflight authored and canonical output/receipt paths; reject aliases with inputs, evaluators, protected files, or sibling outputs; stage outputs privately; validate; compute hashes; commit with recovery; emit a complete receipt tied to the exact committed bytes. Preserve last-good/recovery artifacts when commit or rollback fails.
13. **Report truthfully**: distinguish structural, behavioral, runtime, and perceptual evidence; mark unavailable checks `not-run` or `blocked` rather than implying a pass.

## Legacy compatibility

Treat `skill-improvement` as a deprecated compatibility surface, not a second implementation owner. When an explicit legacy invocation reaches this skill, preserve user-supplied parameters, use `references/legacy-migration.md`, and execute the canonical `skill-improver` workflow. Do not create new `.skill-improvement/` state or maintain a duplicate reviewer/loop.

## Stop conditions

Stop, revert, or return a bounded partial result when: target identity is ambiguous; no safe baseline can be preserved; required source truth is unavailable; a required evaluator cannot be frozen; evaluator/protected inputs change during a candidate; mutation requires blocked fixtures, expected outputs, secrets, or unrelated paths; a required capability is unavailable for a hard gate; a required change gate fails or cannot run; the same objective repair fails to improve after two rounds; output/receipt paths alias inputs/protected paths/sibling outputs; validation/package checks fail; source snapshots no longer match and cannot be re-baselined; or the only route to green weakens a hard gate.

## Output contract

For substantive improvement/hardening runs include:
1. target, mode, objective, baseline identity, runtime capability profile, and final artifact;
2. evaluator contract, frozen inputs/hash, source snapshot identity/verification, baseline/final scores, auxiliary metric, and delta;
3. hypothesis source, selected hypothesis, accepted/rejected/deferred hypotheses, expected mechanism, changed files, validation method, and decision evidence;
4. exact commands with `pass` / `fail` / `not-run` / `blocked` outcomes;
5. structural change-gate result and decision impact;
6. protected paths, rollback/recovery evidence, final frozen candidate hash/identity;
7. canonical termination status/reason, package/install result, authored/canonical output paths, artifact hash, receipt path/status, and last-good preservation result when applicable;
8. evidence-layer summary and residual nondeterminism/risks;
9. for `self-improvement`, controller/baseline/candidate identities, generation ID, recursion limit, last-known-good identity, external-validation status, promotion decision, and self-improvement receipt validation.

## Validation checklist

Before declaring success, verify: the same frozen evaluator produced baseline and final evidence; saturated metrics have auxiliary evidence before improvement claims; source snapshots are verified or deliberately re-baselined; required target validators passed; required structural change gate passed; blocked paths are unchanged; modified scripts were executed or syntax-checked; repair loops respected the bounded stop rule; no template residue/cache/generated report/secret/credential/package artifact entered the target; final candidate was not edited after its final pass; package/output paths passed canonical alias preflight; artifact/receipt hashes refer to the committed bytes; package scope is accurate; and scenario rates are reported only from captured outputs.


## Orchestration boundary

This skill owns bounded improvement experiments and self-improvement generation state. It may use directly related evaluator, hypothesis, or change-gate contracts already declared by this package, but it must not discover, select, or sequence a broad catalog of improvement specialists. A caller/orchestrator may supply additional review evidence; consume that evidence through its declared contract without absorbing the provider's orchestration logic.
