---
name: skill-booster
description: "use when optimizing, improving, benchmarking, hardening, compressing, validating, or packaging an existing chatgpt or agent skill folder or extracted skill.zip through a complete specialist workflow with baseline, benchmark/harness evidence, skill-hypothesis-discovery, skill-change-gate acceptance review, architecture, activation, consistency, documentation, code and script review, security, tests, cleanup, token reduction, hardening, final benchmark, closure, and validated skill.zip delivery; do not use for net-new skill creation without an existing target, generic repository refactors, or unsupported measured-improvement claims"
---

# Skill Booster

## Mission

Optimize one existing skill package end to end with evidence: baseline, frozen evaluator, benchmark/harness signals, hypothesis backlog, bounded patches, change gates, validation, post-stability compression, hardening, package checks, and clear separation of measured facts from checklist judgment.

## Required inputs and defaults

Resolve or infer before mutation:

- `TARGET_SKILL_PATH`: folder or extracted zip with exactly one root `SKILL.md`.
- Mode: `audit-only`, `plan-only`, `apply-optimization`, `validation-only`, or `package`. Full optimization means `apply-optimization`, validation, then packaging when gates pass.
- Objective: activation, output quality, architecture, docs, scripts, security, validation, hygiene, token cost, or complete optimization.
- Writable scope: target folder only unless narrowed.
- Protected paths: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence/reports, old zips, read-only paths, unrelated repos, and frozen evaluator assets.
- Evaluator: target validator/CI, `skill-benchmark`, harness, static validator, or planned evaluator when execution is impossible.
- Final artifact: report, patched folder, validated `skill.zip`, or install-ready package.
- `skill-hypothesis-discovery`: required after baseline evidence; if no delegate is executable, apply its checklist and record evidence.
- `skill-change-gate`: required for candidate acceptance and final regression review; if no delegate is executable, apply its checklist and record evidence.
- Explicit specialist sequence: when the user names required specialists, invoke each available specialist; classify unavailable, blocked, unsafe, or not-applicable passes separately from checklist-only review.

## Mode selection

- `audit-only`: inspect maturity, risks, and candidate hypotheses; no mutation or package claim.
- `plan-only`: produce backlog, sequence, and gates before edits.
- `apply-optimization`: mutate the target with accepted bounded patches, then validate.
- `validation-only`: check an already changed target; write reports outside the target only.
- `package`: build `skill.zip` only from a validated target; repair first only when safe and in scope.

## Resource loading

Load only phase-relevant files:

- [references/optimization-workflow.md](references/optimization-workflow.md): ordered phases and gates.
- [references/specialist-passbook.md](references/specialist-passbook.md): required pass sequence, statuses, and skip rules.
- [references/evaluation-contract.md](references/evaluation-contract.md): freeze rules, metrics, hypothesis records, and change-gate integration.
- [references/mutation-and-safety-policy.md](references/mutation-and-safety-policy.md): allowed edits, blocked paths, rollback, and security floor.
- [references/reporting-contract.md](references/reporting-contract.md): final report sections and evidence language.
- [scripts/validate_skill_booster.py](scripts/validate_skill_booster.py): structural validator and target preflight.
- [scripts/run_activation_harness.py](scripts/run_activation_harness.py): deterministic activation-scenario schema/coverage check; not live LLM precision evidence.
- [scripts/validate_specialist_reconciliation.py](scripts/validate_specialist_reconciliation.py): hard gate for user-required specialist sequence reconciliation before final readiness or package claims.
- [scripts/package_skill.py](scripts/package_skill.py): validates with the booster validator, can enforce a reconciliation ledger, excludes generated artifacts, and builds `skill.zip` outside the target.
- [assets/templates/optimization-report.md.template](assets/templates/optimization-report.md.template): reusable report template.
- [examples/sample-optimization-run.md](examples/sample-optimization-run.md): calibrated compact run.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, and edge coverage.

## Workflow

1. **Preflight and inventory**: confirm one root `SKILL.md`; run `python scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>`; inventory core dirs, validators, packages, and generated files.
2. **Baseline and freeze**: use the strongest available evaluator. Freeze scenarios, expected outputs, scoring config, validator scripts, benchmark inputs, fixtures, generated baseline reports, and blocked paths. Record score, gates, warnings, command, timestamp, and hashes when practical. For compatible activation scenarios, run `python scripts/run_activation_harness.py --scenarios <TARGET_SKILL_PATH>/evals/activation-scenarios.json --json` and label it schema/coverage only.
3. **Specialist sequence**: run, apply by checklist, block, or mark not-applicable for every pass, in order: `skill-creator-juiced`, `skill-benchmark`, `skill-harness`, `skill-hypothesis-discovery`, `skill-improver`, `skill-change-gate`, `skill-package-architecture-review`, `context-architect`, `skill-prompt-and-activation-review`, `prompt-architect`, `skill-consistency-repair`, `documentation-quality`, `karpathy-guidelines`, `security-and-governance-review`, `skill-testing-and-validation`, `skill-cleanup-and-simplification`, `skill-token-efficient`, post-compression `skill-testing-and-validation`, `skill-hardening`, final `skill-change-gate`, final `skill-benchmark`, final `skill-improver`, and final `skill-token-efficient` closure. When the user supplies a required sequence, create a reconciliation ledger with `required_specialists`, `invoked_specialists`, `checklist_only`, `blocked`, `unavailable`, `not_applicable`, and `not_run`. Run `python scripts/validate_specialist_reconciliation.py --ledger <LEDGER_JSON>` before any completion, readiness, or full-sequence claim.
4. **Hypotheses and patches**: generate 5-10 evidence-backed hypotheses, dedupe/rank, select top 3-5 and next 1-3 to test. Apply bounded changes, preferably one hypothesis per patch batch. For each meaningful change, record id, changed files, expected effect, validation, gate decision, accept/reject/revert decision, and evidence. Revert rejected hypotheses unless independently required as a blocking repair.
5. **Validation, compression, hardening**: rerun frozen evaluators and target validators after edits, cleanup, and compression. Token closure checks total, per-file, and matching Markdown-section deltas; local growth must be compressed, accepted as semantic trade-off, or rejected. Never weaken activation, safety, validation, output, stop, routing, hypothesis, or evidence duties.
6. **Package and close**: package only when validation passes and required specialist reconciliation allows finalization. Use `python scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --report <REPORT_PATH>`; add `--reconciliation-ledger <LEDGER_JSON>` when the user required an explicit specialist sequence. Archive outside the target, with one top-level folder, no caches/reports/generated evidence/secrets/old zips, and passing validation before sharing.

## Output contract

Final reports must include:

1. target skill path, mode, and objective;
2. baseline inventory, evaluator, score, gates, warnings, frozen inputs, and protected blocked paths;
3. required specialist sequence reconciliation, including:
   - required count;
   - invoked-skill count;
   - checklist-only count;
   - blocked count;
   - unavailable count;
   - not-applicable count;
   - not-run count;
   - full sequence satisfied: yes/no;
   - finalization allowed: yes/no;
4. specialist pass ledger with status, execution_type, and evidence;
5. hypothesis-discovery status, candidate backlog count, selected hypotheses, and deferred hypotheses;
6. accepted/rejected hypotheses with files, expected effect, validation, change-gate decision, and evidence;
7. required repairs kept without measured improvement;
8. files changed by phase;
9. protected paths respected statement;
10. validation commands and pass/fail/not-run outcomes;
11. before/after benchmark or static score when measured;
12. skill-change-gate and final skill-change-gate status;
13. final benchmark result;
14. total/local token deltas, local trade-offs, and final token-efficiency closure;
15. package path only when `skill.zip` exists and package validation passed;
16. remaining risks, assumptions, rollback notes, and next hypothesis or no-mutation recommendation.

Use `measured` only for executed commands, validators, scenario results, package checks, or supplied data.

Use `observed`, `inferred`, `planned`, `checklist-only`, or `blocked` for other evidence.

Do not claim benchmark improvement, specialist execution, security review, scenario pass rate, package readiness, full specialist sequence satisfaction, token reduction, or final readiness without evidence.

Manual checklist review must never be described as a specialist invocation.

## Stop conditions

Stop before mutation when the target has zero/multiple root `SKILL.md` files; edits touch protected paths; measured improvement is required but no evaluator can be frozen; source truth is missing and a patch would invent facts; no evidence-backed hypothesis exists; `skill-change-gate` finds an unfixable blocking regression; validation fails and cannot be fixed in scope; or packaging would include secrets, caches, generated reports/evidence, old zips, or files outside the final skill folder.

## Finalization checklist

Before completion, confirm: required specialist reconciliation passed when supplied; frontmatter is lowercase hyphen-case; activation/non-activation/ambiguous/edge scenarios exist or are planned; local refs resolve; resources are integrated or retained; no scaffold, caches, old packages, secrets, or generated noise remain; modified scripts ran or blockers are stated; discovery precedes improvement claims; material patches have gate decisions; compression was revalidated; local token growth is compressed or accepted as semantic trade-off; final token closure preserves activation, safety, validation, output, stop, routing, and evidence duties; final gate has no blocking regression; final benchmark separates measured from planned checks; package validation passes before sharing `skill.zip`.
