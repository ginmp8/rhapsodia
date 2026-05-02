---
name: skill-booster
description: use when asked to optimize, improve, benchmark, harden, compress, validate, or package an existing chatgpt or agent skill by orchestrating a complete specialist workflow over a target skill folder or zip. use for skill-target optimization, activation repair, architecture review, prompt and output-contract refinement, documentation, code/script review, security governance, tests, validation, cleanup, token reduction, hardening, benchmark comparison, and final skill.zip delivery. do not use for net-new skill creation without an existing target skill, generic repository refactors, or unsupported claims of measured improvement.
---

# Skill Booster

## Mission

Optimize an existing skill package end to end. Receive one target skill, establish a baseline, run the full specialist optimization workflow, apply bounded improvements, revalidate after every material change, reduce tokens only after behavior is stable, harden/package the final skill, and report measured evidence separately from judgment.

Use this skill as the coordinator. It does not replace specialist skills; it invokes or applies their checks in a controlled order and records each pass.

## Required Inputs

Resolve or infer before mutation:

1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one root `SKILL.md`.
2. Desired mode: `audit-only`, `plan-only`, `apply-optimization`, `validation-only`, or `package`.
3. Optimization objective: activation, output quality, architecture, documentation, scripts, security, validation, package hygiene, token cost, or complete optimization.
4. Writable scope: default to target skill folder only.
5. Blocked paths: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence, old zips, and user-declared read-only files.
6. Evaluation method: existing evaluator, `skill-benchmark`, scenario harness, static validator, or planned evaluator when execution is impossible.
7. Final artifact: report only, patched folder, validated `skill.zip`, or install-ready package.

Default when underspecified: run complete optimization in a safe target-folder-only scope, make one bounded patch batch per phase, validate after changes, package only when validation passes.

## Resource Loading

Load only the branch needed for the current phase:

- [references/optimization-workflow.md](references/optimization-workflow.md): full ordered workflow, phase gates, and sequencing.
- [references/specialist-passbook.md](references/specialist-passbook.md): required specialist passes, inputs, outputs, and skip rules.
- [references/evaluation-contract.md](references/evaluation-contract.md): baseline/final metrics, evaluator freeze rules, scenario contract, and accept/reject logic.
- [references/mutation-and-safety-policy.md](references/mutation-and-safety-policy.md): allowed edits, blocked paths, rollback, and safety boundaries.
- [references/reporting-contract.md](references/reporting-contract.md): final report sections and evidence language.
- [scripts/validate_skill_booster.py](scripts/validate_skill_booster.py): structural validator for this skill and target-skill preflight checks.
- [assets/templates/optimization-report.md.template](assets/templates/optimization-report.md.template): reusable final report template.
- [examples/sample-optimization-run.md](examples/sample-optimization-run.md): calibrated example of a complete run.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, and edge scenarios for this skill.

## Workflow

1. **Preflight**
   - Confirm exactly one target `SKILL.md`.
   - Run `python scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>` when filesystem access is available.
   - Inventory `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, `evals/`, validators, reports, and package files.

2. **Baseline and freeze**
   - Establish baseline using the strongest available evaluator.
   - Freeze evaluator inputs before editing: scenarios, scoring config, expected outputs, scripts, reports, and benchmark data.
   - Record score, gates, warnings, command, timestamp, and blocked paths.

3. **Run specialist passes in order**
   - `skill-creator-juiced`: handle major redesign decisions, production-ready skill-quality orchestration, and escalation when the target needs router/mode/split redesign rather than ordinary optimization.
   - `skill-improver`: coordinate objective, hypothesis budget, baseline/final comparison, and accept/reject decisions.
   - `skill-benchmark`: score current maturity and final maturity.
   - `skill-harness`: create or run repeatable activation, non-activation, ambiguous, edge, regression, and output-conformance scenarios.
   - `skill-package-architecture-review`: decide unified skill, modes, router, split, resource layout, and progressive loading.
   - `context-architect`: map cross-file impact when scripts, references, generated artifacts, or repo context affect changes.
   - `skill-prompt-and-activation-review`: refine frontmatter description, triggers, exclusions, ambiguity handling, stop conditions, and output contract.
   - `prompt-architect`: refine complex instruction assets, prompt bodies, or agent instructions when present.
   - `skill-consistency-repair`: repair contradictions, stale claims, broken local references, and resource integration gaps.
   - `documentation-quality`: improve references, examples, templates, usage docs, and script-facing documentation.
   - `karpathy-guidelines`: review bundled scripts, validators, commands, technical examples, and implementation complexity.
   - `security-and-governance-review`: audit secrets, sensitive logging, unsafe commands, dependency risk, tool authority, and governance boundaries.
   - `skill-testing-and-validation`: run validators, lint, smoke tests, package checks, and modified scripts.
   - `skill-cleanup-and-simplification`: remove scaffold, duplicates, obsolete resources, caches, generated noise, and unused files after integration is assessed.
   - `skill-token-efficient`: reduce token cost only after behavior, safety, architecture, and output contracts are stable.
   - `skill-testing-and-validation`: revalidate after compression.
   - `skill-hardening`: run final readiness, validation, package hygiene, and delivery checks.
   - `skill-benchmark`: rerun final benchmark against baseline.
   - `skill-improver`: decide final accepted/rejected hypotheses and close the report.

4. **Patch discipline**
   - Apply one explicit hypothesis per patch batch.
   - Keep `SKILL.md` as compact control plane; move branch detail to `references/`.
   - Use scripts only for deterministic validation or repeatable transformations.
   - Keep assets only when copied, filled, rendered, or used in outputs.
   - Do not alter frozen evaluators, fixtures, expected outputs, generated evidence, secrets, or unrelated files.

5. **Validate and package**
   - Re-run the frozen evaluator after each material patch batch.
   - Re-run target validators and package checks after cleanup and after token compression.
   - Package as `skill.zip` only when gates pass and archive scope is the final target skill folder.

## Specialist Usage Policy

A complete optimization run must execute or explicitly account for every specialist listed in the workflow, including `skill-creator-juiced` as the escalation/design-governance pass. If a specialist cannot be invoked directly in the current environment, apply the specialist's local checklist from [references/specialist-passbook.md](references/specialist-passbook.md) and mark the pass as `applied-by-checklist`. If a pass is genuinely not applicable, mark it `not-applicable` with evidence.

Do not fabricate pass/fail status. Use `planned`, `not-run`, `blocked`, `applied-by-checklist`, `pass`, or `fail` when measured evidence is unavailable.

## Output Contract

Final responses and reports include:

1. target skill path and mode;
2. baseline inventory, evaluator, score, gates, and warnings;
3. frozen inputs and blocked paths protected;
4. specialist pass ledger with status and evidence;
5. accepted and rejected hypotheses;
6. files changed by phase;
7. validation commands and pass/fail outcomes;
8. before/after benchmark or static score when measured;
9. token before/after when measured;
10. final package path only when `skill.zip` exists and package validation passed;
11. remaining risks, assumptions, rollback notes, and next recommended hypothesis.

## Stop Conditions

Stop before mutation when:

- the target has zero or multiple root `SKILL.md` files and the correct root is unclear;
- the requested change requires editing blocked paths;
- no evaluator can be frozen and the user specifically requires measured improvement;
- the target depends on unavailable source truth and the change would invent domain facts;
- validation fails after a structural change and cannot be fixed within target scope;
- package creation would include secrets, caches, generated reports, old zips, or files outside the final skill folder.

## Finalization Checklist

Before declaring completion:

- target frontmatter has lowercase hyphen-case `name` and a specific `description`;
- activation, non-activation, ambiguous, and edge scenarios exist or are logged as planned;
- `SKILL.md` contains mission, workflow, resource loading, output contract, validation, and stop conditions;
- every referenced local file exists;
- important resources are referenced, script-consumed, template-filled, validated, or intentionally asset-only;
- no scaffold markers, caches, old packages, secrets, or generated noise remain;
- modified scripts were run once or the blocker is reported;
- token compression was followed by validation;
- final benchmark/report distinguishes executed evidence from planned checks;
- package validation passes before sharing `skill.zip`.
