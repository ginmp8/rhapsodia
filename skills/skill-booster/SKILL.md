---
name: skill-booster
description: "use when optimizing, improving, benchmarking, hardening, compressing, validating, or packaging an existing chatgpt or agent skill folder or extracted skill.zip through a complete specialist workflow with baseline, benchmark/harness evidence, skill-hypothesis-discovery, skill-change-gate acceptance review, architecture, activation, consistency, documentation, code and script review, security, tests, cleanup, token reduction, hardening, final benchmark, closure, and validated skill.zip delivery; do not use for net-new skill creation without an existing target, generic repository refactors, or unsupported measured-improvement claims"
---

# Skill Booster

## Mission

Optimize one existing skill package end to end. Establish a baseline, freeze evaluators, gather benchmark and harness evidence, run `skill-hypothesis-discovery` to produce a prioritized improvement backlog, apply bounded patches through `skill-improver`, pass candidate changes through `skill-change-gate`, validate after material changes, compress only after behavior is stable, harden/package only after gates pass, and separate measured evidence from judgment.

## Required inputs and defaults

Resolve or infer before mutation:

1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one root `SKILL.md`.
2. Mode: `audit-only`, `plan-only`, `apply-optimization`, `validation-only`, or `package`.
3. Objective: activation, output quality, architecture, docs, scripts, security, validation, hygiene, token cost, or complete optimization.
4. Writable scope: target folder only unless narrowed.
5. Blocked: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence, old zips, read-only paths, unrelated repos.
6. Evaluator: existing validator, `skill-benchmark`, harness, static validator, or planned evaluator when execution is impossible.
7. Final artifact: report, patched folder, validated `skill.zip`, or install-ready package.
8. Hypothesis-discovery policy: `required`, `advisory`, or `not-available`; default to `required` for full optimization after baseline benchmark/harness evidence exists. If unavailable, derive and rank hypotheses by checklist and mark the pass `applied-by-checklist` only when evidence is recorded.
9. Change-gate policy: `required`, `advisory`, or `not-available`; default to `required` for full optimization and classify unavailable gate execution as `applied-by-checklist` only when the checklist evidence is recorded.

Default: complete optimization in target-scope only; one bounded patch batch per phase; run `skill-hypothesis-discovery` or its checklist before `skill-improver` when no user-supplied hypothesis backlog exists; run `skill-change-gate` or its checklist before accepting material candidate changes; validate after changes; package only after folder and archive checks pass.

## Resource loading

Load only the branch needed for the current phase:

- [references/optimization-workflow.md](references/optimization-workflow.md): ordered phases and gates.
- [references/specialist-passbook.md](references/specialist-passbook.md): pass checklist, statuses, and skip rules.
- [references/evaluation-contract.md](references/evaluation-contract.md): freeze rules, metrics, hypothesis-discovery contract, acceptance, skill-change-gate integration, saturated-score handling.
- [references/mutation-and-safety-policy.md](references/mutation-and-safety-policy.md): allowed edits, blocked paths, rollback, security floor.
- [references/reporting-contract.md](references/reporting-contract.md): final report sections and evidence language.
- [scripts/validate_skill_booster.py](scripts/validate_skill_booster.py): structural validator and target preflight.
- [scripts/package_skill.py](scripts/package_skill.py): validates then builds `skill.zip` outside the target folder.
- [assets/templates/optimization-report.md.template](assets/templates/optimization-report.md.template): reusable report template.
- [examples/sample-optimization-run.md](examples/sample-optimization-run.md): compact calibrated run.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, and edge coverage.

## Workflow

1. **Preflight**: confirm one root `SKILL.md`; run `python scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>`; inventory `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, `evals/`, reports, validators, and package files.
2. **Baseline and freeze**: use the strongest available evaluator; freeze scenarios, expected outputs, scoring config, validator scripts, benchmark inputs, generated baseline reports, and blocked paths; record score, gates, warnings, command, timestamp, and hashes when available.
3. **Specialist sequence**: run or explicitly account for every pass in this order: `skill-creator-juiced`, `skill-benchmark`, `skill-harness`, `skill-hypothesis-discovery`, `skill-improver`, `skill-change-gate`, `skill-package-architecture-review`, `context-architect`, `skill-prompt-and-activation-review`, `prompt-architect`, `skill-consistency-repair`, `documentation-quality`, `karpathy-guidelines`, `security-and-governance-review`, `skill-testing-and-validation`, `skill-cleanup-and-simplification`, `skill-token-efficient`, `skill-testing-and-validation`, `skill-hardening`, final `skill-change-gate`, final `skill-benchmark`, final `skill-improver`, final `skill-token-efficient` closure.
4. **Patch discipline**: one hypothesis per patch batch; edit only allowed target files; keep `SKILL.md` as control plane; move branch detail to `references/`; use scripts only for deterministic validation or packaging; keep assets only when copied, filled, rendered, validated, or intentionally asset-only.
5. **Validate and package**: rerun the frozen evaluator and target validators after material changes, cleanup, and token compression. Package with `python scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --report <REPORT_PATH>` only when gates pass and archive scope is the final skill folder.

## Specialist usage policy

A complete run must execute, apply by checklist, or classify every pass in [references/specialist-passbook.md](references/specialist-passbook.md). Use status `planned`, `not-run`, `blocked`, `not-applicable`, `applied-by-checklist`, `pass`, or `fail`. Never fabricate benchmark, validation, scenario, security, package, or token-reduction evidence.

## Output contract

Final reports include:

1. target skill path, mode, and objective;
2. baseline inventory, evaluator, score, gates, warnings, frozen inputs, and protected blocked paths;
3. specialist pass ledger with status and evidence;
4. hypothesis-discovery backlog summary, selected hypotheses, and accepted/rejected hypotheses with files, expected effect, validation, change-gate decision, evidence;
5. files changed by phase;
6. validation commands and pass/fail/not-run outcomes;
7. before/after benchmark or static score when measured;
8. skill-hypothesis-discovery status, candidate backlog count, and selected hypotheses;
9. skill-change-gate and final skill-change-gate status;
10. token before/after plus final token-efficiency closure status;
11. package path only when `skill.zip` exists and package validation passed;
12. remaining risks, assumptions, rollback notes, and next hypothesis.

## Stop conditions

Stop before mutation when the target has zero or multiple root `SKILL.md` files; the requested change touches blocked paths; no evaluator can be frozen and measured improvement is required; source truth is unavailable and the change would invent domain facts; no evidence-based hypothesis can be derived and the user did not provide one; `skill-change-gate` reports a blocking regression that cannot be fixed in scope; validation fails after structural change and cannot be fixed in scope; or packaging would include secrets, caches, generated reports, old zips, or files outside the final skill folder.

## Finalization checklist

Before declaring completion: frontmatter is lowercase hyphen-case with a specific description; activation/non-activation/ambiguous/edge scenarios exist or are planned; all local references resolve; important resources are integrated or intentionally retained; no scaffold markers, caches, old packages, secrets, or generated noise remain; modified scripts ran or blockers are stated; hypothesis discovery produced a backlog or an explicit no-mutation recommendation before measured improvement attempts; material patches have a `skill-change-gate` decision or applied checklist; token compression is followed by validation; final token closure preserves activation, safety, validation, output, stop, routing, and evidence duties; final `skill-change-gate` has no blocking regression; final benchmark separates executed evidence from planned checks; package validation passes before sharing `skill.zip`.
