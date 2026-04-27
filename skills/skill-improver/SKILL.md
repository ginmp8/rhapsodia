---
name: skill-improver
description: hypothesis-driven improvement workflow for chatgpt, codex, claude, or copilot skills. use when asked to improve, harden, benchmark, iterate on, self-improve, package, or run autonomous experiments against a target skill using explicit hypotheses, frozen metrics, acceptance gates, rollback, and repeatable evals. do not use for generic code refactoring, skill creation from scratch, or unbounded autonomous edits without a sandbox, metric, budget, and rollback plan.
---

# Skill Improver

## Purpose

Improve a target skill through controlled experiments. Treat every candidate change as a falsifiable hypothesis: baseline first, freeze the evaluator, apply one bounded patch, re-run the same evaluator, accept only if the configured metric improves and all gates pass, otherwise revert or report rejection.

This `SKILL.md` is the control plane. Load detailed references only for the branch being executed.

## Scope boundary

Use this skill for:

- benchmarking, auditing, or scoring an existing skill package;
- manually improving a skill with measured before/after evidence;
- running a bounded autonomous or Codex-driven improvement loop;
- hardening `skill-improver` itself using self-improvement safeguards;
- validating, installing, or packaging an improved skill after gates pass.

Do not use this skill for:

- creating a new skill from scratch; use a skill-creation workflow instead;
- general repository refactoring unrelated to a skill package;
- editing evaluator fixtures, expected outputs, benchmark lockfiles, generated reports used as evidence, secrets, or paths outside the allowed mutation scope;
- claiming improvement from a saturated metric that merely stayed passing;
- running unbounded or yolo-style automation outside an externally disposable sandbox.

## Required inputs

Resolve or conservatively default these before mutating a target skill:

1. `TARGET_SKILL_PATH`: folder or extracted zip containing exactly one target skill.
2. Mode: `benchmark-only`, `manual-patch`, `automated-loop`, `package-install`, or `self-improvement`.
3. Evaluator mode: existing command, `skill-benchmark`, hybrid static plus behavioral results, or generate benchmark first.
4. Frozen metric contract: score, direction, minimum delta, required status/gates, benchmark locks, and blocked paths.
5. Budget: maximum iterations, wall-clock limit, or single manual patch.
6. Allowed mutation scope and blocked paths.
7. Safety mode: sandboxed local run, isolated container, CI runner, or manual patch review.
8. Final artifact requirement: patch report, installed folder, or package zip.

When details are missing, proceed with conservative defaults: one bounded manual patch or up to three automated iterations, `--min-delta 1.0`, target-folder-only mutation, evaluator/fixture/report/secrets blocked, and manual patch review unless a stronger sandbox is explicitly available.

## Mode selection

| User intent | Mode | Required evidence | Primary output | Closure gate |
|---|---|---|---|---|
| Benchmark, audit, or score a skill | `benchmark-only` | Static report and supplied scenario results if any | Findings and canonical report | Evaluator ran or blocker stated |
| Improve a skill without automation | `manual-patch` | Baseline, frozen evaluator, changed files, final score | Accepted or rejected patch summary | Score improves and gates pass |
| Run an autonomous or Codex loop | `automated-loop` | Clean working copy, evaluator hash, budget, rollback log | Iteration report | No benchmark drift and accepted patch passes gates |
| Package or install an improved skill | `package-install` | Final validation, backup path, writable destination or zip path | Installed folder or `skill.zip` | Validator and package checks pass |
| Improve `skill-improver` itself | `self-improvement` | Separate working copy, original backup, blocked evals/reports | Same as manual patch plus self-risk notes | Auxiliary non-saturated evidence improves or hardening delta is explicit |

## Reference loading map

Load only what the run needs:

- `references/evaluation-contract.md`: evaluator schema, freeze rules, acceptance logic, and gate policy.
- `references/benchmark-integration.md`: `skill-benchmark` integration, report parsing, and saturated-score handling.
- `references/hypothesis-catalog.md`: choose one bounded hypothesis per iteration.
- `references/autoresearch-adaptation.md`: map research-loop mechanics to skill package work.
- `references/execution-runbook.md`: CLI modes, default commands, self-improvement safeguards, packaging flow, and rollback rules.
- `references/harness-design.md`: complete harness design, scenario metrics, and auxiliary non-saturated evidence.
- `references/report-template.md`: final improvement report shape.
- `evals/skill-improver-scenarios.json`: planned activation, negative, ambiguous, edge, and regression scenarios; do not mutate during an improvement run unless the user requested benchmark-design work.
- `assets/templates/improvement-run-report.md.template`: run report template consumed by `scripts/skill_improver_loop.py` when writing improvement evidence.
- `assets/templates/patch-decision-record.md.template`: per-iteration decision template consumed by `scripts/skill_improver_loop.py` for accepted or rejected hypotheses.
- `scripts/skill_improver_loop.py`: bounded automated runner when the user requests an autonomous or Codex loop.
- `scripts/static_skill_score.py`: starter structural evaluator when no richer benchmark exists; treat saturated results as gates only.

Do not add or preserve unused asset templates. A template is considered used when it is consumed by a script, explicitly referenced by `SKILL.md` or a reference, copied or filled during a declared workflow, or validated by a package/checklist gate. When a benchmark flags supporting resources as weakly integrated, prefer integration before deletion: add workflow references, usage rules, writer/validator coverage, or clearer loading conditions before removing a useful resource. Remove or migrate assets only when they are placeholders, duplicated, obsolete, or purely explanatory content better suited to `references/`.

## Workflow

1. **Inspect**
   - Read the target `SKILL.md` first.
   - Inventory `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, `evals/`, validators, and existing reports.
   - Identify the objective: activation quality, output conformance, validation strength, context efficiency, maintainability, safety, or packaging reliability.

2. **Prepare and freeze evaluation**
   - Establish the evaluator command and metric contract before editing.
   - Hash or lock evaluator scripts, scenario suites, expected outputs, scoring configuration, and benchmark inputs.
   - If the primary score is saturated, keep it as a required gate and define a non-saturated auxiliary signal before claiming improvement.

3. **Measure baseline**
   - Run the evaluator before mutation.
   - Record score, status, gates, command, report path, evaluator hash, timestamp, and blocked paths.
   - If the evaluator cannot run, fix or define the evaluation harness before improving the target.

4. **Select one hypothesis**
   - Use `references/hypothesis-catalog.md` or derive one explicit hypothesis from the observed weakness.
   - State mechanism, target files, expected metric effect, and validation gate.
   - Keep the patch minimal and scoped.

5. **Apply candidate change**
   - Edit only allowed paths.
   - Do not modify blocked evaluator files, scenario fixtures, expected outputs, benchmark reports, generated evidence, `.git`, caches, or secrets.
   - Keep `SKILL.md` compact; move branch-specific detail to references and use `assets/templates/` for repeatable artifact skeletons that are rendered, copied, or filled by a declared workflow.

6. **Evaluate and decide**
   - Re-run the same frozen evaluator.
   - Reject if the evaluator hash changed, blocked paths changed, required gates fail, or the score does not meet `min_delta`.
   - Accept only with measured evidence and record rejected hypotheses so they are not retried.

7. **Validate and package when requested**
   - Run the target package validator when present.
   - For this skill, run `scripts/validate_skill_improver_package.py` and, when producing a zip, `scripts/package_skill.py`.
   - Package only the final skill folder, excluding caches, temporary reports, benchmark outputs, secrets, and existing zip files.

8. **Report truthfully**
   - State measured versus proposed evidence.
   - Include commands, scores, gates, changed files, protected blocked paths, package or install path, rollback notes, and residual risks.

## Stop conditions

Stop, revert, or report a blocker when:

- the target path has zero or multiple `SKILL.md` files;
- no executable or frozen evaluator exists for an improvement run;
- the requested mutation scope includes blocked evaluator fixtures, generated benchmark evidence, secrets, or unrelated repository paths;
- the benchmark, scenario suite, or expected outputs changed during a candidate patch;
- a candidate modifies files outside allowed scope;
- a required gate fails after the patch;
- packaging validation fails;
- the user asks for unbounded automation without an acknowledged disposable sandbox.

## Output contract

For any improvement or hardening run, final output must include:

1. Target skill and mode.
2. Baseline score, final score, auxiliary metric result when used, and delta.
3. Evaluator mode, frozen inputs, benchmark hash or lock status, and report path.
4. Accepted and rejected hypotheses with evidence.
5. Files changed and blocked paths protected.
6. Commands executed and pass/fail outcomes.
7. Final gates/status.
8. Installation or package result, including backup and rollback path when applicable.
9. Remaining risks and next recommended hypothesis.

## Validation checklist

Before declaring success:

- baseline and final scores came from the same frozen evaluator;
- saturated primary metrics were paired with auxiliary evidence before an improvement claim;
- all required gates passed;
- target-specific validators passed;
- blocked paths were unchanged;
- no unconsumed placeholder scaffolding, cache, generated report, secret, or package artifact was added to the target folder;
- package/install scope is stated accurately;
- measured scenario rates are reported only when prompt outputs were actually captured.
