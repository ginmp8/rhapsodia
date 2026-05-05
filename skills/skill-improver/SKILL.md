---
name: skill-improver
description: use for existing chatgpt, claude, copilot, or codex skill packages when asked to benchmark, audit, improve, harden, self-improve, validate, package, install, or run bounded hypothesis-driven loops with frozen evaluators, evidence-backed hypothesis discovery, measurable deltas, change gates, rollback, and reports. use skill-hypothesis-discovery or a supplied backlog when no bounded hypothesis is provided or metrics are saturated. do not use for new skills, generic repo refactors, ordinary code changes, or unbounded automation without sandbox, metric, budget, and rollback.
---

# Skill Improver

## Purpose

Improve an existing skill through controlled experiments: inspect, freeze an evaluator, measure baseline, select or discover an evidence-backed bounded hypothesis, apply one candidate patch, re-run the same evaluator, and accept only when the metric improves, evaluator gates pass, and the structural change gate reports no blocking regression. Otherwise revert or report rejection. Keep `SKILL.md` as the compact control plane and load references only for the active branch.

## Scope

Use for existing skill packages when the task is benchmarking, auditing, scoring, manual improvement, bounded Codex/autonomous improvement, self-improvement with safeguards, validation, installation, or packaging.

Do not use for new skill creation, generic repository refactors, ordinary application-code work, edits to evaluator fixtures or expected outputs, generated evidence, secrets, unrelated paths, or unbounded/yolo automation outside an acknowledged disposable sandbox.

## Inputs and default policy

Resolve before mutation:
1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one target `SKILL.md`.
2. Mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
3. Evaluator and metric contract: command, `skill-benchmark`, hybrid/static benchmark, score direction, minimum delta, required gates, locks, blocked paths.
4. Hypothesis source: user-supplied hypothesis, JSON backlog, built-in catalog, or `skill-hypothesis-discovery` result. Use discovery when no bounded hypothesis is supplied, when benchmark scores are saturated, or when the next test is unclear.
5. Budget and safety mode: iteration/time budget, sandbox or manual-review posture, allowed mutation scope.
6. Change gate policy: `disabled`, `advisory`, or `required`; default to `required` for automated-loop and self-improvement when a gate command or `skill-change-gate` review is available.
7. Final artifact: report, patched folder, installed folder, or package zip.

Defaults: one bounded manual patch or max three automated iterations; `--min-delta 1.0`; target-folder-only mutation; use a supplied hypothesis/backlog first, then `skill-hypothesis-discovery` when available, then the built-in hypothesis catalog as fallback; evaluator files, fixtures, reports, generated evidence, packages, caches, `.git`, credentials, and secrets blocked; change gate required for autonomous acceptance when available and advisory for manual patches; manual review unless a stronger sandbox is available.

## Mode selection

- `benchmark-only`: run an evaluator, report findings, and stop without patching.
- `manual-patch`: baseline -> freeze -> use supplied/discovered hypothesis -> one minimal patch -> final score -> accept/reject.
- `automated-loop`: require clean working copy, evaluator hash, hypothesis source or discovery fallback, budget, rollback log, and blocked paths.
- `package-install`: validate first; then write to the requested destination or produce `skill.zip`.
- `self-improvement`: require separate working copy, original backup, blocked evals/reports, and self-risk notes; accept only with non-saturated auxiliary evidence or explicit hardening delta.

## Resource loading

Load only what the branch needs:
- `references/evaluation-contract.md`: evaluator schema, freeze rules, acceptance, metric gates, hypothesis-backlog policy, and structural change-gate policy.
- `references/benchmark-integration.md`: `skill-benchmark`, report parsing, saturated-score handling.
- `references/hypothesis-catalog.md`: built-in fallback hypotheses, discovery handoff rules, severity triage, change-gate hypotheses, loop-control hypotheses, and expected evidence.
- `skill-hypothesis-discovery` or a compatible hypothesis backlog JSON: optional evidence-backed hypothesis source. Load or run only when no bounded hypothesis was supplied, metrics are saturated, or the next candidate is unclear.
- `references/autoresearch-adaptation.md`: autonomous loop mechanics mapped to skill packages.
- `references/execution-runbook.md`: CLI modes, defaults, self-improvement, packaging, rollback.
- `references/harness-design.md`: scenario metrics and auxiliary evidence.
- `references/report-template.md`: final report contract including change-gate evidence.
- `evals/skill-improver-scenarios.json`: planned activation, negative, ambiguous, edge, and regression suite; do not mutate during candidate optimization unless benchmark design is the task.
- `assets/templates/improvement-run-report.md.template` and `assets/templates/patch-decision-record.md.template`: templates consumed by `scripts/skill_improver_loop.py`.
- `scripts/static_skill_score.py`: deterministic starter evaluator; saturated scores are gates only.
- `skill-change-gate` or a compatible `--change-gate-command`: optional external gate for candidate structural regressions. Load or run only during candidate acceptance decisions.
- `scripts/validate_skill_improver_package.py` and `scripts/package_skill.py`: package validation and zip creation.

Keep templates only when rendered, copied, filled, script-consumed, or validated. Integrate useful resources before deleting; remove placeholders, duplicates, obsolete examples, caches, generated reports, old zips, and unused starter files only after classification.

## Workflow

1. **Inspect**: read target `SKILL.md`; inventory agents, references, scripts, assets/templates, examples, evals, validators, reports, package artifacts, and known risks.
2. **Freeze evaluation**: define evaluator command and metric contract; hash/lock evaluator scripts, scenarios, expected outputs, scoring config, benchmark inputs, and blocked paths. If the primary score is saturated, keep it as a gate and add an auxiliary metric before claiming improvement.
3. **Measure baseline**: record score, status, gates, command, report path, evaluator hash, timestamp, blocked paths, and unresolved risks.
4. **Triage reviewer findings when present**: classify findings as critical, major, or minor; fix critical and major issues before polish; evaluate minor items for functional value and false positives before editing.
5. **Discover or load hypotheses when needed**: if the user did not provide a bounded hypothesis, if the evaluator is saturated, or if reviewer findings point in multiple directions, use `skill-hypothesis-discovery` or a supplied backlog to generate 5-10 candidates, rank them, and select the next 1-3 testable hypotheses. Do not mutate during discovery.
6. **Select one hypothesis**: state mechanism, evidence signal, files, expected effect, validation method, accept/reject rule, and rollback plan. Prefer the highest-ranked discovered hypothesis; use the built-in catalog only as fallback.
7. **Apply candidate**: edit only allowed paths; keep branch detail in references; never weaken evaluator, safety, activation, output, or package gates.
8. **Evaluate and decide**: re-run the frozen evaluator, then apply the structural change gate when policy requires or advises it. Reject if the evaluator hash changes, blocked paths change, evaluator gates fail, the score misses the threshold, or the change gate reports a blocking regression in loading, activation, scope, safety, references, validation, packaging, evidence discipline, or output contract. Record rejected hypotheses and non-blocking trade-offs.
9. **Handle loop lifecycle**: for long-running loops, honor configured stop files between iterations; cancellation preserves already accepted target changes and does not fabricate completion.
10. **Validate and package**: run target validators and script smoke checks. Package only after validation passes and exclude caches, generated reports, benchmark outputs, secrets, credentials, old zips, and files outside the final skill folder.
11. **Report truthfully**: separate measured evidence from planned or checklist-only findings.

## Stop conditions

Stop, revert, or report a blocker when the target has zero or multiple root `SKILL.md` files; no executable/frozen evaluator exists; requested mutation touches blocked fixtures, expected outputs, generated evidence, secrets, or unrelated paths; evaluator inputs change during a candidate patch; required evaluator gates fail; no bounded hypothesis can be selected from supplied input, discovery, or built-in fallback; a required change gate fails or cannot run; validation/package checks fail; or the user requests unbounded automation without a disposable sandbox and explicit budget.

## Output contract

For improvement or hardening runs include:
1. target skill, path, mode, objective, and final artifact;
2. baseline and final score, auxiliary metric if used, delta, evaluator mode, frozen inputs, hash/lock status, and report path;
3. hypothesis source: supplied, discovery backlog, built-in catalog, or fallback, including discovery status, candidate count, selected hypothesis, and deferred hypotheses when available;
4. accepted and rejected hypotheses with files changed, expected effect, validation method, decision, and evidence;
5. commands executed with pass/fail outcomes;
6. structural change gate status: `pass`, `pass-with-warnings`, `fail`, or `not-run`, plus blocking regressions, material concerns, accepted trade-offs, and decision impact;
7. blocked paths protected and rollback notes;
8. final evaluator gates/status, package or install result, remaining risks, and next recommended hypothesis.

## Validation checklist

Before declaring success, verify: the same frozen evaluator produced baseline and final scores; saturated metrics have auxiliary evidence; hypothesis source and selection rationale are recorded; discovery outputs are treated as planned evidence until tested; required evaluator gates and target validators passed; required change gate passed or non-blocking findings are recorded; blocked paths are unchanged; modified scripts ran or syntax-checked; no template residue, cache, generated report, secret, credential, or package artifact was added; package scope is accurate; scenario rates are reported only from captured prompt outputs.
