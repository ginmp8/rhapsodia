---
name: skill-improver
description: use for existing chatgpt, claude, copilot, or codex skill packages when asked to benchmark, audit, improve, harden, self-improve, validate, package, install, or run bounded hypothesis-driven loops with frozen evaluators, measurable deltas, gates, rollback, and reports. do not use for new skills, generic repo refactors, or unbounded automation without sandbox, metric, budget, and rollback.
---

# Skill Improver

## Purpose

Improve an existing skill through controlled experiments. Baseline first; freeze the evaluator; apply one bounded hypothesis; re-run the same evaluator; accept only when the configured metric improves and all gates pass; otherwise revert or report rejection. `SKILL.md` is the control plane; load references only for the active branch.

## Scope

Use for:
- benchmarking, auditing, or scoring an existing skill package;
- manual skill improvement with measured before/after evidence;
- bounded autonomous or Codex-driven improvement loops;
- hardening `skill-improver` itself with self-improvement safeguards;
- validation, installation, or packaging after gates pass.

Do not use for:
- creating a new skill; use a skill-creation workflow;
- generic repository refactors unrelated to a skill package;
- editing evaluator fixtures, expected outputs, benchmark lockfiles, generated evidence reports, secrets, or paths outside allowed mutation scope;
- claiming improvement from a saturated metric that only stayed passing;
- unbounded/yolo automation outside an explicitly acknowledged disposable sandbox.

## Required inputs and defaults

Resolve before mutation:
1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one target skill.
2. Mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
3. Evaluator: existing command, `skill-benchmark`, hybrid static+behavioral results, or generate benchmark first.
4. Frozen metric contract: score, direction, minimum delta, required status/gates, locks, blocked paths.
5. Budget: max iterations, wall-clock limit, or single manual patch.
6. Allowed mutation scope and blocked paths.
7. Safety mode: sandboxed local run, isolated container, CI runner, or manual review.
8. Final artifact: patch report, installed folder, or package zip.

Missing details default to: one bounded manual patch or max three automated iterations; `--min-delta 1.0`; target-folder-only edits; evaluator/fixture/report/secrets blocked; manual patch review unless a stronger sandbox is available.

## Modes

- `benchmark-only`: audit/score; output findings and canonical report; close when evaluator ran or blocker is stated.
- `manual-patch`: baseline -> frozen evaluator -> minimal patch -> final score; accept only on score improvement plus gates.
- `automated-loop`: require clean copy, evaluator hash, budget, rollback log; accept only with no benchmark drift and passing gates.
- `package-install`: require final validation, backup path, writable destination or zip path; close after validator/package checks pass.
- `self-improvement`: require separate working copy, original backup, blocked evals/reports, and self-risk notes; accept only with non-saturated auxiliary evidence or explicit hardening delta.

## Load map

Load only as needed:
- `references/evaluation-contract.md`: evaluator schema, freeze rules, acceptance, gates.
- `references/benchmark-integration.md`: `skill-benchmark`, report parsing, saturated-score handling.
- `references/hypothesis-catalog.md`: one bounded hypothesis per iteration.
- `references/autoresearch-adaptation.md`: research-loop mechanics mapped to skill packages.
- `references/execution-runbook.md`: CLI modes, defaults, self-improvement, packaging, rollback.
- `references/harness-design.md`: full harness, scenario metrics, auxiliary non-saturated evidence.
- `references/report-template.md`: final report shape.
- `evals/skill-improver-scenarios.json`: planned activation/negative/ambiguous/edge/regression suite; do not mutate during improvement unless benchmark design was requested.
- `assets/templates/improvement-run-report.md.template`: run report template consumed by `scripts/skill_improver_loop.py`.
- `assets/templates/patch-decision-record.md.template`: accepted/rejected hypothesis record consumed by `scripts/skill_improver_loop.py`.
- `scripts/skill_improver_loop.py`: bounded automated runner for autonomous/Codex loops.
- `scripts/static_skill_score.py`: starter structural evaluator when no richer benchmark exists; saturated results are gates only.

Resource rule: do not keep unused asset templates. A template is used only when consumed by a script, referenced by `SKILL.md`/reference, copied or filled in a declared workflow, or validated by a package/checklist gate. If a benchmark flags weak integration, prefer integration before deletion. Remove/migrate assets only when placeholders, duplicates, obsolete, or purely explanatory content better suited to `references/`.

## Workflow

1. **Inspect**: read target `SKILL.md` first; inventory `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, `evals/`, validators, reports; identify objective: activation, output conformance, validation, context efficiency, maintainability, safety, or packaging.
2. **Freeze evaluation**: define evaluator command and metric contract before editing; hash/lock evaluator scripts, scenarios, expected outputs, scoring config, and benchmark inputs; if the primary score is saturated, keep it as a gate and define a non-saturated auxiliary signal before claiming improvement.
3. **Measure baseline**: run evaluator pre-mutation; record score, status, gates, command, report path, evaluator hash, timestamp, blocked paths. If no evaluator can run, first fix or define the harness.
4. **Select one hypothesis**: use `references/hypothesis-catalog.md` or derive one explicit hypothesis; state mechanism, target files, expected metric effect, and validation gate; keep scope minimal.
5. **Apply candidate**: edit only allowed paths. Do not modify blocked evaluator files, fixtures, expected outputs, benchmark reports, generated evidence, `.git`, caches, or secrets. Keep `SKILL.md` compact; move branch detail to references; keep `assets/templates/` for repeatable skeletons that a declared workflow renders, copies, or fills.
6. **Evaluate and decide**: re-run the same frozen evaluator. Reject if evaluator hash changed, blocked paths changed, gates fail, or score misses `min_delta`. Accept only with measured evidence; record rejected hypotheses to avoid repeats.
7. **Validate/package when requested**: run target validator. For this skill run `scripts/validate_skill_improver_package.py`; when zipping, run `scripts/package_skill.py`. Package only the final skill folder and exclude caches, temp reports, benchmark outputs, secrets, and old zips.
8. **Report truthfully**: separate measured facts from proposals; include commands, scores, gates, changed files, protected blocked paths, package/install path, rollback notes, and residual risks.

## Stop conditions

Stop, revert, or report a blocker when:
- target path has zero or multiple `SKILL.md` files;
- no executable/frozen evaluator exists for an improvement run;
- requested mutation includes blocked fixtures, generated evidence, secrets, or unrelated paths;
- benchmark, scenario suite, expected outputs, or evaluator change during a candidate patch;
- candidate changes files outside allowed scope;
- a required gate or packaging validation fails;
- user requests unbounded automation without an acknowledged disposable sandbox.

## Output contract

For improvement or hardening runs include:
1. target skill and mode;
2. baseline score, final score, auxiliary metric if used, and delta;
3. evaluator mode, frozen inputs, benchmark hash/lock status, report path;
4. accepted and rejected hypotheses with evidence;
5. files changed and blocked paths protected;
6. commands executed with pass/fail outcomes;
7. final gates/status;
8. installation/package result, including backup and rollback path when applicable;
9. remaining risks and next recommended hypothesis.

## Validation checklist

Before declaring success, verify: same frozen evaluator produced baseline/final scores; saturated primary metrics have auxiliary evidence before improvement claims; all required gates and target validators passed; blocked paths unchanged; no placeholder scaffolding, cache, generated report, secret, or package artifact was added; package/install scope is accurate; scenario rates are reported only from captured prompt outputs.
