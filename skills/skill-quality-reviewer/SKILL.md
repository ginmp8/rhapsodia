---
name: skill-quality-reviewer
description: review, audit, score, compare, or validate chatgpt and compatible agent skill packages, folders, zips, skill.md files, references, scripts, evals, and prior review reports. use when the user wants evidence-based findings about activation, ownership, architecture, workflow correctness, legacy coupling, obsolete compatibility, migration residue, duplicated contracts, runtime peer coupling, structural noise, resource integration, contradictions, validation gaps, package hygiene, token efficiency, or prompt-ready remediation instructions. produce severity-ranked findings, an evidence-based scorecard, legacy and ownership matrices when applicable, a readiness verdict, and a self-contained correction input. do not use to implement fixes, create new skills, review ordinary application code, or perform security audits.
---

# Skill Quality Reviewer

## Mission

Review a skill package as an operational system, not as isolated prose. Find real defects, inconsistencies, activation failures, dead workflow branches, broken resources, unsupported claims, validation gaps, historical coupling, obsolete compatibility, migration residue, ownership drift, and package-quality regressions. Produce an auditable report that can be used directly as the input or prompt for correcting the target skill.

## Core Rules

- Review only by default. Do not mutate the target skill, rewrite files, package a replacement, or claim a fix was applied unless the user explicitly requests a separate correction phase.
- Prefer evidence over preference. Tie every material finding to a file, section, link, script result, scenario, command output, consumer, contract, or explicit missing artifact.
- Distinguish `confirmed`, `likely`, `needs verification`, `planned`, and `out of scope` evidence.
- Inspect the skill as a connected package: activation description, instructions, modes, references, scripts, assets, examples, evals, validators, agent metadata, packaging rules, handoffs, migrations, changelogs, and peer-skill boundaries.
- Hunt failure paths, not only style defects. Check routing, ordering, unreachable branches, contradictory duties, hidden dependencies, stale resources, evaluator drift, invalid assumptions, outputs that cannot satisfy their own contract, and normal paths that silently preserve old behavior.
- Reconstruct the current canonical contract before classifying historical content. Do not assume the newest-looking file, highest version, or most repeated statement is authoritative.
- Classify legacy candidates as `current`, `migration-only`, `obsolete`, `duplicate`, `contradictory`, `noise`, or `blocked`.
- Treat keyword and filename matches as discovery signals only. Do not confirm or recommend removal without tracing current owners, writers, readers, imports, tests, validators, examples, packaging, and supported migration paths.
- Require explicit isolation for `migration-only` behavior. Normal activation and execution must not silently fall back to old schemas, aliases, paths, states, or versions.
- Recommend the smallest sufficient correction. Do not turn a local defect into a broad redesign unless the evidence shows an architectural cause.
- Do not penalize an unconventional design merely because it differs from a preferred template. Penalize only behavior, maintainability, evidence, or package-integrity consequences.
- Do not treat optional folders as mandatory unless the target platform, target skill, or declared contract requires them.
- Keep checklist scoring separate from executed validation. Never describe a static score as a measured behavioral benchmark.
- Produce a self-contained correction input that does not depend on this conversation, hidden reasoning, or unstated context.

## Security Exclusion

Security is intentionally outside this skill's review rubric. Do not score secrets, authorization, permissions, threat models, dependency vulnerabilities, sandbox escape, or abuse resistance. When scripts exist, review them only for correctness, determinism, error handling, path assumptions, runtime coupling, integration, and package behavior. Route an explicit security request to a dedicated security-review skill.

## Modes

| Mode | Trigger | Primary output |
|---|---|---|
| `full-review` | complete audit, score, readiness, or correction prompt | full report, weighted scorecard, findings, legacy assessment, correction input |
| `legacy-audit` | legacy cleanup, historical coupling, obsolete compatibility, migration residue, old aliases, permissive fallback, ownership drift, or structural noise | classification matrices, ownership and compatibility analysis, severity-ranked findings, correction input |
| `quick-triage` | quick check, first pass, small `SKILL.md`, or limited files | up to five highest-value findings and next checks |
| `compare-versions` | before/after folders, candidate patch, or two packages | regressions, improvements, unresolved defects, legacy reintroduction or removal, acceptance verdict |
| `report-validation` | validate a prior skill-review report or remediation input | missing evidence, unsupported claims, incomplete findings, prompt defects, legacy-classification gaps |

Default to `full-review`. Select `legacy-audit` when the user explicitly asks to remove or classify historical behavior, compatibility, migrations, aliases, old flows, changelog noise, or cross-skill coupling. Use `quick-triage` only when the user explicitly asks for a short review or the supplied target is small. Use `compare-versions` only when both baselines are inspectable.

## Required Inputs and Defaults

Use the strongest available target:

- skill folder, extracted ZIP, ZIP archive, repository path, or supplied files;
- intended purpose, owner role, and expected activation surface when available;
- current contract sources, supported versions, migration commitments, and ownership map when legacy decisions depend on them;
- requested mode, output language, strictness, and scoring expectations;
- known failures, previous reports, validation commands, protected files, or peer packages when supplied.

Defaults:

- infer the target purpose from frontmatter and package contents;
- answer in the user's language;
- review all inspectable files under the selected skill root;
- treat missing compatibility or consumer evidence as `blocked` instead of preserving or removing by assumption;
- keep generated reports outside the target package;
- do not require a correction implementation to complete the review.

Stop and request the correct target only when zero or multiple candidate root `SKILL.md` files make the review subject ambiguous. If a partial target is intentional, proceed and state the limitation. For multi-skill ecosystem review, keep a separate package map and score per skill before evaluating shared contracts.

## Resource Loading

Load only what the active mode needs:

- [`references/review-workflow.md`](references/review-workflow.md): ordered investigation and closure workflow.
- [`references/review-rubric.md`](references/review-rubric.md): dimensions, defect taxonomy, scorecard, and readiness gates.
- [`references/legacy-and-compatibility-audit.md`](references/legacy-and-compatibility-audit.md): legacy classifications, migration gates, audit surfaces, technical searches, ownership calibration, and closure criteria.
- [`references/finding-model.md`](references/finding-model.md): severity, evidence labels, finding quality bar, legacy classification, and confidence rules.
- [`references/report-contract.md`](references/report-contract.md): full-review, legacy-audit, quick-triage, comparison, and report-validation formats.
- [`references/correction-input-contract.md`](references/correction-input-contract.md): copy-paste-ready remediation prompt contract.
- [`scripts/inspect_skill_package.py`](scripts/inspect_skill_package.py): deterministic package preflight and discovery-only legacy-signal inventory.
- [`scripts/validate_review_report.py`](scripts/validate_review_report.py): deterministic validation of the generated Markdown report.
- [`assets/templates/skill-review-report.md.template`](assets/templates/skill-review-report.md.template): fillable full-report skeleton.
- [`examples/review-scenarios.md`](examples/review-scenarios.md): calibration examples when severity, legacy classification, or verdict is uncertain.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation and boundary scenarios; do not claim live activation metrics from this file.

## Workflow

1. **Classify the target and mode.** Identify the skill root, requested depth, intended output, and whether the task is review-only, legacy audit, comparison, or report validation.
2. **Run deterministic preflight when possible.** Execute `python scripts/inspect_skill_package.py <target> --json-out <report.json>`. Treat structural findings as evidence and `legacy_signal_summary` entries as discovery candidates, not semantic verdicts.
3. **Inventory the package.** Record `SKILL.md`, `agents/`, references, scripts, assets, examples, evals, validators, package builders, changelogs, generated files, peer dependencies, and uninspected surfaces.
4. **Reconstruct intended current behavior.** State the skill's owner role, target artifacts, activation prompts, non-activation boundaries, modes, inputs, outputs, tools, handoffs, stop conditions, current identifiers, schemas, states, and supported versions.
5. **Identify canonical sources.** Map each important concept to its current machine-readable schema, validator, `SKILL.md` rule, canonical reference, validated fixture, owner, and consumer. Treat disagreements as candidates rather than resolving them silently.
6. **Define invariants.** Identify what must remain true for correct activation, routing, execution, authority, evidence, output, validation, migration isolation, compatibility, and packaging.
7. **Run structural and semantic evidence passes.** Use deterministic inspection for objective package signals, then trace behavior, current contracts, ownership, consumers, compatibility paths, and failure hypotheses. Treat keyword or filename matches as discovery only.
8. **Review activation and boundaries.** Check false-positive and false-negative risks, ambiguous prompts, adjacent-skill overlap, contradictory trigger text, and missing handoffs.
9. **Review architecture and progressive loading.** Check cohesion, mode-versus-router decisions, control-plane size, reference depth, resource ownership, and hidden runtime dependencies.
10. **Review workflow correctness.** Trace each core mode from intake through evidence, decisions, outputs, validation, stop conditions, and closure. Hunt unreachable steps, order defects, circular duties, missing transitions, and branches that cannot satisfy their output contract.
11. **Audit legacy, compatibility, and structural noise.** Apply `references/legacy-and-compatibility-audit.md`. Trace every material candidate to writers, readers, imports, tests, validators, examples, packaging, and migration entry points; classify it before recommending preserve, isolate, consolidate, remove, reject, or gather evidence.
12. **Review package consistency.** Cross-check frontmatter, `SKILL.md`, references, scripts, templates, examples, evals, metadata, validators, changelogs, and packaging rules for drift or contradiction.
13. **Review evidence and validation.** Separate executed checks from planned scenarios. Check whether validators actually test claimed properties, whether old formats are explicitly rejected, and whether evidence can be mutated by the workflow being evaluated.
14. **Generate bounded defect hypotheses.** Prioritize activation failure, core workflow failure, current-contract contradiction, implicit legacy acceptance, ownership transfer, runtime peer coupling, broken resources, validator drift, package invalidity, and repeated-context dilution. Confirm, reject, or retain each as a named gap.
15. **Score with evidence.** Apply `references/review-rubric.md`. Record each dimension's evidence, raw judgment, weighted score, and any gate override. Label the score `static review judgment` unless a supplied or executed evaluator supports more.
16. **Apply gates and decide the provisional verdict.** Resolve score/verdict contradictions, decision-critical `blocked` items, unresolved common-path majors, and unsupported behavioral claims before drafting remediation.
17. **Write findings and matrices.** Order findings by severity. Each material finding must satisfy `references/finding-model.md`. Include legacy classification, ownership, compatibility, and runtime-coupling matrices when applicable; include them unconditionally in `legacy-audit` mode.
18. **Build the correction input.** Convert accepted findings into ordered, bounded remediation instructions using `references/correction-input-contract.md`. Preserve current behavior, remove obsolete compatibility, isolate valid migrations, replace acceptance tests with rejection tests where support ended, and prohibit scope drift.
19. **Validate the report when possible.** Execute `python scripts/validate_review_report.py <report.md>`. Repair report-shape failures without weakening findings.
20. **Close honestly.** State verdict, score type, inspected coverage, executed commands, classification counts, unresolved questions, and whether the correction input is ready to use.

## Review Priorities

Inspect in this order:

1. package root and parseability;
2. current canonical sources, ownership, and supported compatibility;
3. activation and non-activation boundaries;
4. core workflow correctness and output feasibility;
5. implicit legacy acceptance, migration leakage, aliases, state translation, old paths, and runtime peer coupling;
6. contradictions, duplicated contracts, and ownership drift;
7. broken or orphaned resources;
8. validation, rejection tests, and evidence discipline;
9. package hygiene, changelog discipline, and deterministic tooling;
10. documentation clarity and token efficiency;
11. cosmetic style only after behavioral risks.

## Output Contract

Use `references/report-contract.md`.

Every substantive review must include:

1. target, mode, scope, assumptions, and uninspected surfaces;
2. reconstructed current skill contract and canonical sources;
3. behavioral and authority invariants;
4. weighted scorecard with evidence and gate effects;
5. severity-ranked findings with evidence, failure path, impact, smallest fix, acceptance criteria, and validation;
6. legacy and compatibility assessment with classification counts and blocked decisions;
7. rejected hypotheses, positive signals, and validation gaps;
8. prioritized remediation plan;
9. self-contained correction input;
10. verdict and next review gate.

In `legacy-audit` mode, also require legacy classification, ownership, compatibility, and runtime-coupling matrices. Do not claim that no legacy exists merely because keyword searches returned no matches.

## Stop Conditions

Stop, narrow, or return `NEEDS_MORE_CONTEXT` when:

- the target has zero or multiple ambiguous root `SKILL.md` files;
- the current canonical contract cannot be reconstructed and the review would invent intended behavior;
- compatibility, consumer, or migration evidence is essential to a removal decision and unavailable; classify the item `blocked` instead of guessing;
- two sources claim current authority and no evidence resolves the conflict;
- a requested score or readiness claim requires behavioral execution that was not supplied or run;
- a prior report lacks enough target evidence to validate its findings;
- the user requests direct implementation rather than review; hand the correction input to a skill-improvement workflow;
- the request is primarily a security audit.

Do not stop merely because the package is large. Bound the inspected scope, report coverage, and continue with the highest-impact surfaces.
