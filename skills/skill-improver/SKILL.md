---
name: skill-improver
description: use for existing chatgpt, claude, copilot, or codex skill packages when asked to benchmark, audit, improve, harden, self-improve, validate, package, install, or run bounded hypothesis-driven loops with frozen evaluators, measurable deltas, gates, rollback, and reports. do not use for new skills, generic repo refactors, ordinary code changes, or unbounded automation without sandbox, metric, budget, and rollback.
---

# Skill Improver

## Purpose

Improve an existing skill through controlled experiments: inspect, freeze an evaluator, measure baseline, apply one bounded hypothesis, re-run the same evaluator, accept only when the metric improves and gates pass, otherwise revert or report rejection. Keep `SKILL.md` as the compact control plane and load references only for the active branch.

## Scope

Use for existing skill packages when the task is benchmarking, auditing, scoring, manual improvement, bounded Codex/autonomous improvement, self-improvement with safeguards, validation, installation, or packaging.

Do not use for new skill creation, generic repository refactors, ordinary application-code work, edits to evaluator fixtures or expected outputs, generated evidence, secrets, unrelated paths, or unbounded/yolo automation outside an acknowledged disposable sandbox.

## Inputs and default policy

Resolve before mutation:
1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one target `SKILL.md`.
2. Mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
3. Evaluator and metric contract: command, `skill-benchmark`, hybrid/static benchmark, score direction, minimum delta, required gates, locks, blocked paths.
4. Budget and safety mode: iteration/time budget, sandbox or manual-review posture, allowed mutation scope.
5. Final artifact: report, patched folder, installed folder, or package zip.

Defaults: one bounded manual patch or max three automated iterations; `--min-delta 1.0`; target-folder-only mutation; evaluator files, fixtures, reports, generated evidence, packages, caches, `.git`, credentials, and secrets blocked; manual review unless a stronger sandbox is available.

## Mode selection

- `benchmark-only`: run an evaluator, report findings, and stop without patching.
- `manual-patch`: baseline -> freeze -> one minimal patch -> final score -> accept/reject.
- `automated-loop`: require clean working copy, evaluator hash, budget, rollback log, and blocked paths.
- `package-install`: validate first; then write to the requested destination or produce `skill.zip`.
- `self-improvement`: require separate working copy, original backup, blocked evals/reports, and self-risk notes; accept only with non-saturated auxiliary evidence or explicit hardening delta.

## Resource loading

Load only what the branch needs:
- `references/evaluation-contract.md`: evaluator schema, freeze rules, acceptance, gates.
- `references/benchmark-integration.md`: `skill-benchmark`, report parsing, saturated-score handling.
- `references/hypothesis-catalog.md`: bounded hypotheses and expected evidence.
- `references/autoresearch-adaptation.md`: autonomous loop mechanics mapped to skill packages.
- `references/execution-runbook.md`: CLI modes, defaults, self-improvement, packaging, rollback.
- `references/harness-design.md`: scenario metrics and auxiliary evidence.
- `references/report-template.md`: final report contract.
- `evals/skill-improver-scenarios.json`: planned activation, negative, ambiguous, edge, and regression suite; do not mutate during candidate optimization unless benchmark design is the task.
- `assets/templates/improvement-run-report.md.template` and `assets/templates/patch-decision-record.md.template`: templates consumed by `scripts/skill_improver_loop.py`.
- `scripts/static_skill_score.py`: deterministic starter evaluator; saturated scores are gates only.
- `scripts/validate_skill_improver_package.py` and `scripts/package_skill.py`: package validation and zip creation.

Keep templates only when rendered, copied, filled, script-consumed, or validated. Integrate useful resources before deleting; remove placeholders, duplicates, obsolete examples, caches, generated reports, old zips, and scaffold only after classification.

## Workflow

1. **Inspect**: read target `SKILL.md`; inventory agents, references, scripts, assets/templates, examples, evals, validators, reports, package artifacts, and known risks.
2. **Freeze evaluation**: define evaluator command and metric contract; hash/lock evaluator scripts, scenarios, expected outputs, scoring config, benchmark inputs, and blocked paths. If the primary score is saturated, keep it as a gate and add an auxiliary metric before claiming improvement.
3. **Measure baseline**: record score, status, gates, command, report path, evaluator hash, timestamp, blocked paths, and unresolved risks.
4. **Select one hypothesis**: state mechanism, files, expected effect, validation method, accept/reject rule, and rollback plan.
5. **Apply candidate**: edit only allowed paths; keep branch detail in references; never weaken evaluator, safety, activation, output, or package gates.
6. **Evaluate and decide**: re-run the frozen evaluator. Reject if the evaluator hash changes, blocked paths change, gates fail, the score misses the threshold, or safety/output behavior regresses. Record rejected hypotheses.
7. **Validate and package**: run target validators and script smoke checks. Package only after validation passes and exclude caches, generated reports, benchmark outputs, secrets, credentials, old zips, and files outside the final skill folder.
8. **Report truthfully**: separate measured evidence from planned or checklist-only findings.

## Stop conditions

Stop, revert, or report a blocker when the target has zero or multiple root `SKILL.md` files; no executable/frozen evaluator exists; requested mutation touches blocked fixtures, expected outputs, generated evidence, secrets, or unrelated paths; evaluator inputs change during a candidate patch; required gates fail; validation/package checks fail; or the user requests unbounded automation without a disposable sandbox and explicit budget.

## Output contract

For improvement or hardening runs include:
1. target skill, path, mode, objective, and final artifact;
2. baseline and final score, auxiliary metric if used, delta, evaluator mode, frozen inputs, hash/lock status, and report path;
3. accepted and rejected hypotheses with files changed, expected effect, validation method, decision, and evidence;
4. commands executed with pass/fail outcomes;
5. blocked paths protected and rollback notes;
6. final gates/status, package or install result, remaining risks, and next recommended hypothesis.

## Validation checklist

Before declaring success, verify: the same frozen evaluator produced baseline and final scores; saturated metrics have auxiliary evidence; required gates and target validators passed; blocked paths are unchanged; modified scripts ran or syntax-checked; no placeholder scaffold, cache, generated report, secret, credential, or package artifact was added; package scope is accurate; scenario rates are reported only from captured prompt outputs.
