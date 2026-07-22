---
name: skill-quality-reviewer
description: Review, audit, score, compare, or validate ChatGPT and compatible agent skill packages, folders, ZIPs, SKILL.md files, references, scripts, evals, and prior review reports. Use when the user wants evidence-based findings about activation, scope, architecture, workflow correctness, resource integration, contradictions, broken references, validation gaps, package hygiene, token efficiency, or prompt-ready remediation instructions. Produce severity-ranked findings, a weighted scorecard, a readiness verdict, and a self-contained correction input. Do not use to implement fixes, create new skills, review ordinary application code, or perform security audits.
---

# Skill Quality Reviewer

## Mission

Review a skill package as an operational system, not as isolated prose. Find real defects, inconsistencies, activation failures, dead workflow branches, broken resources, unsupported claims, validation gaps, and package-quality regressions. Produce an auditable report that can be used directly as the input or prompt for correcting the target skill.

## Core Rules

- Review only by default. Do not mutate the target skill, rewrite files, package a replacement, or claim a fix was applied unless the user explicitly requests a separate correction phase.
- Prefer evidence over preference. Tie every material finding to a file, section, link, script result, scenario, command output, or explicit missing artifact.
- Distinguish `confirmed`, `likely`, `needs verification`, `planned`, and `out of scope` evidence.
- Inspect the skill as a connected package: activation description, instructions, modes, references, scripts, assets, examples, evals, validators, agent metadata, packaging rules, and handoffs.
- Hunt failure paths, not only style defects. Check routing, ordering, unreachable branches, contradictory duties, hidden dependencies, stale resources, evaluator drift, invalid assumptions, and outputs that cannot satisfy their own contract.
- Recommend the smallest sufficient correction. Do not turn a local defect into a broad redesign unless the evidence shows an architectural cause.
- Do not penalize an unconventional design merely because it differs from a preferred template. Penalize only behavior, maintainability, evidence, or package-integrity consequences.
- Do not treat optional folders as mandatory unless the target platform, target skill, or declared contract requires them.
- Keep checklist scoring separate from executed validation. Never describe a static score as a measured behavioral benchmark.
- Produce a self-contained correction input that does not depend on this conversation, hidden reasoning, or unstated context.

## Security Exclusion

Security is intentionally outside this skill's review rubric. Do not score secrets, authorization, permissions, threat models, dependency vulnerabilities, sandbox escape, or abuse resistance. When scripts exist, review them only for correctness, determinism, error handling, path assumptions, integration, and package behavior. Route an explicit security request to a dedicated security-review skill.

## Modes

| Mode | Trigger | Primary output |
|---|---|---|
| `full-review` | complete audit, score, readiness, or correction prompt | full report, weighted scorecard, findings, correction input |
| `quick-triage` | quick check, first pass, small `SKILL.md`, or limited files | up to five highest-value findings and next checks |
| `compare-versions` | before/after folders, candidate patch, or two packages | regressions, improvements, unresolved defects, acceptance verdict |
| `report-validation` | validate a prior skill-review report or remediation input | missing evidence, unsupported claims, incomplete findings, prompt defects |

Default to `full-review`. Use `quick-triage` only when the user explicitly asks for a short review or the supplied target is small. Use `compare-versions` only when both baselines are inspectable.

## Required Inputs and Defaults

Use the strongest available target:

- skill folder, extracted ZIP, ZIP archive, repository path, or supplied files;
- intended purpose and expected activation surface when available;
- requested mode, output language, strictness, and scoring expectations;
- known failures, previous reports, validation commands, or protected files when supplied.

Defaults:

- infer the target purpose from frontmatter and package contents;
- answer in the user's language;
- review all inspectable files under the selected skill root;
- treat missing context as a named gap instead of inventing intent;
- keep generated reports outside the target package;
- do not require a correction implementation to complete the review.

Stop and request the correct target only when zero or multiple candidate root `SKILL.md` files make the review subject ambiguous. If a partial target is intentional, proceed and state the limitation.

## Resource Loading

Load only what the active mode needs:

- [`references/review-workflow.md`](references/review-workflow.md): ordered investigation and closure workflow.
- [`references/review-rubric.md`](references/review-rubric.md): dimensions, defect taxonomy, scorecard, and readiness gates.
- [`references/finding-model.md`](references/finding-model.md): severity, evidence labels, finding quality bar, and confidence rules.
- [`references/report-contract.md`](references/report-contract.md): full-review, quick-triage, comparison, and report-validation formats.
- [`references/correction-input-contract.md`](references/correction-input-contract.md): copy-paste-ready remediation prompt contract.
- [`scripts/inspect_skill_package.py`](scripts/inspect_skill_package.py): deterministic package preflight for objective structural signals.
- [`scripts/validate_review_report.py`](scripts/validate_review_report.py): deterministic validation of the generated Markdown report.
- [`assets/templates/skill-review-report.md.template`](assets/templates/skill-review-report.md.template): fillable full-report skeleton.
- [`examples/review-scenarios.md`](examples/review-scenarios.md): calibration examples when severity or verdict is uncertain.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation and boundary scenarios; do not claim live activation metrics from this file.

## Workflow

1. **Classify the target and mode.** Identify the skill root, requested depth, intended output, and whether the task is review-only, comparison, or report validation.
2. **Run deterministic preflight when possible.** Execute `python scripts/inspect_skill_package.py <target> --json-out <report.json>`. Treat its output as structural evidence, not a semantic verdict.
3. **Inventory the package.** Record `SKILL.md`, `agents/`, references, scripts, assets, examples, evals, validators, package builders, generated files, and uninspected surfaces.
4. **Reconstruct intended behavior.** State the skill's owner role, target artifacts, activation prompts, non-activation boundaries, modes, inputs, outputs, tools, handoffs, and stop conditions.
5. **Define invariants.** Identify what must remain true for correct activation, routing, execution, evidence, output, validation, and packaging.
6. **Review activation and boundaries.** Check false-positive and false-negative risks, ambiguous prompts, adjacent-skill overlap, contradictory trigger text, and missing handoffs.
7. **Review architecture and progressive loading.** Check cohesion, mode-versus-router decisions, control-plane size, reference depth, resource ownership, and hidden dependencies.
8. **Review workflow correctness.** Trace each core mode from intake through evidence, decisions, outputs, validation, stop conditions, and closure. Hunt unreachable steps, order defects, circular duties, missing transitions, and branches that cannot satisfy their output contract.
9. **Review package consistency.** Cross-check frontmatter, `SKILL.md`, references, scripts, templates, examples, evals, metadata, validators, and packaging rules for drift or contradiction.
10. **Review evidence and validation.** Separate executed checks from planned scenarios. Check whether validators actually test claimed properties and whether evidence can be mutated by the workflow being evaluated.
11. **Generate bounded defect hypotheses.** Prioritize activation failure, core workflow failure, broken resources, contradictory contracts, validator drift, package invalidity, and repeated-context dilution. Confirm, reject, or retain each as a named gap.
12. **Score with evidence.** Apply `references/review-rubric.md`. Record each dimension's evidence, raw judgment, weighted score, and any gate override. Label the score `static review judgment` unless a supplied or executed evaluator supports more.
13. **Write findings.** Order by severity. Each material finding must satisfy `references/finding-model.md`.
14. **Build the correction input.** Convert accepted findings into ordered, bounded remediation instructions using `references/correction-input-contract.md`. Preserve non-goals, protected paths, validation commands, and completion evidence.
15. **Validate the report when possible.** Execute `python scripts/validate_review_report.py <report.md>`. Repair report-shape failures without weakening findings.
16. **Close honestly.** State verdict, score type, inspected coverage, executed commands, unresolved questions, and whether the correction input is ready to use.

## Review Priorities

Inspect in this order:

1. package root and parseability;
2. activation and non-activation boundaries;
3. core workflow correctness and output feasibility;
4. contradictions and ownership drift;
5. broken or orphaned resources;
6. validation and evidence discipline;
7. package hygiene and deterministic tooling;
8. documentation clarity and token efficiency;
9. cosmetic style only after behavioral risks.

## Output Contract

Use `references/report-contract.md`.

Every substantive review must include:

1. target, mode, assumptions, and scope inspected;
2. reconstructed purpose and behavioral invariants;
3. executed and unexecuted validation evidence;
4. weighted scorecard with evidence per dimension;
5. severity-ranked findings with location, evidence, impact, smallest fix, acceptance criteria, and validation;
6. validation gaps and uninspected surfaces;
7. final readiness verdict;
8. a self-contained correction input suitable for another AI or correction workflow.

For `compare-versions`, distinguish introduced regressions, resolved defects, unchanged defects, and uncertain differences. Do not infer improvement from file-count or token-count changes alone.

## Verdicts

Choose exactly one:

- ✅ `READY`: no blocker or unresolved major finding; evidence and package gates are adequate for the declared scope.
- 🟡 `READY_WITH_COMMENTS`: only bounded minor, nit, or explicitly accepted concerns remain.
- 🔴 `REWORK_REQUIRED`: at least one blocker or unresolved major defect prevents reliable use or packaging.
- 🟣 `NEEDS_MORE_CONTEXT`: essential target, intent, baseline, or evidence is missing and could change the decision.

A high numeric score cannot override a blocker. Missing behavioral execution does not automatically block a static review, but it must prevent claims of measured activation quality or benchmark readiness.

## Stop Conditions

Stop, narrow, or return `NEEDS_MORE_CONTEXT` when:

- the target root is ambiguous;
- the supplied files are too partial to reconstruct the requested review surface;
- a claimed defect lacks evidence and cannot be downgraded to a question;
- comparison is requested without both inspectable versions;
- the user asks for a security verdict under this skill;
- the user asks for implementation rather than review and correction input;
- the report would claim behavioral scores, pass rates, or readiness without executed or supplied evidence.

## Package Maintenance

When maintaining this skill package:

1. mutate only files under `skill-quality-reviewer`;
2. keep `SKILL.md` as the compact control plane;
3. run `python scripts/inspect_skill_package.py . --json-out /tmp/skill-quality-reviewer-preflight.json`;
4. run `python -m py_compile scripts/inspect_skill_package.py scripts/validate_review_report.py`;
5. validate the package with the active skill-package validator;
6. package only after validation passes, with one top-level `skill-quality-reviewer/` folder and no caches, reports, or old archives.
