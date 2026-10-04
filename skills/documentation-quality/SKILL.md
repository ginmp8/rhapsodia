---
name: documentation-quality
description: use when asked to create, review, reorganize, evaluate, or improve technical documentation inside skill packages or repositories, including reference files, readmes, usage guides, script and validator documentation, examples, tutorials, and human-oriented technical guides. improves clarity, structure, accessibility, technical accuracy, examples, and flow while preserving domain terms, contracts, source truth, scope boundaries, and context economy. do not use for full target-skill activation ownership, hardening, benchmarking, code implementation, or mcp-dependent workflows.
---

# Documentation Quality

## Core rule

Improve documentation against inspectable evidence. Target files, scripts, validators, examples, READMEs, contracts, and executed command output are source truth. Never invent behavior, commands, validation results, ownership boundaries, user success, or visual details. Repeated reviews using the same target, evidence, mode, content intent, and rubric should produce materially comparable findings; editorial wording may vary.

## Required inputs

Resolve or infer before material edits:

- target files/directories;
- primary mode and any secondary modes;
- intended audience and task;
- content intent when it materially changes the quality criteria;
- requested outcome: review, direct edits, or both;
- source truth available for verification;
- target-native documentation validators/linters when discoverable;
- whether reader/task validation is requested or feasible;
- whether a durable report or machine-readable receipt is required.

Resolve ambiguity first only when target, audience, task, content intent, or outcome materially changes the work.

## Mode selection

| Request | Mode |
|---|---|
| Review `references/` | `reference-doc-review` |
| Review README/guide/main usage docs | `readme-review` |
| Document scripts, commands, parameters, outputs, errors, validators | `script-documentation` |
| Improve examples/tutorials/scenarios | `example-improvement` |
| Improve Markdown structure/accessibility | `markdown-accessibility` |
| Evaluate accuracy, completeness, flow, task success | `technical-content-evaluation` |
| Reorganize docs without duplication | `documentation-restructure` |
| Produce a durable review report | `documentation-report` |

Use multiple modes only when needed; keep one primary mode for ordering criteria and reporting.

## Content intent

Treat review mode and document purpose as separate dimensions. When purpose is material, resolve `content_kind` as `tutorial`, `how-to`, `reference`, `explanation`, `quickstart`, `troubleshooting`, `mixed`, or `unspecified`, then load [`references/content-type-contracts.md`](references/content-type-contracts.md). Do not force a single type onto intentionally mixed content.

## Progressive loading

Load only what the active branch needs:

- [`references/review-contract.md`](references/review-contract.md): evidence labels, finding schema, severity, comparison identity, completion gates, and bounded repair.
- [`references/documentation-quality-rubric.md`](references/documentation-quality-rubric.md): versioned quality criteria and mode mapping.
- [`references/content-type-contracts.md`](references/content-type-contracts.md): content-purpose obligations and mixed-content rules.
- [`references/reader-task-validation.md`](references/reader-task-validation.md): optional reader/task success evidence and comparison rules.
- [`references/language-and-global-readiness.md`](references/language-and-global-readiness.md): clarity, terminology, ambiguity, and conditional global-readiness review.
- [`references/markdown-accessibility-checklist.md`](references/markdown-accessibility-checklist.md): source-level and rendered accessibility boundaries.
- [`references/reference-file-patterns.md`](references/reference-file-patterns.md): Skill references, context economy, restructure patterns.
- [`assets/templates/documentation-review-report.md.template`](assets/templates/documentation-review-report.md.template): durable review shape.
- [`examples/skill-documentation-before-after.md`](examples/skill-documentation-before-after.md): rewrite calibration.

Load the review contract for substantive reviews, validated direct edits, durable reports, or before/after claims.

## Verification helpers

Resolve an available Python 3 launcher and denote it `<PYTHON>`. Do not require a particular executable name, shell, installation path, or vendor-private API. Bundled helpers use only the Python standard library.

Prefer validation evidence in this order when applicable: exact user-supplied command; command frozen in an approved plan/review contract; target-native documentation validator/linter; bundled generic helper. Do not replace a stronger target-native check with an easier generic check merely to obtain a pass.

- [`scripts/check_documentation_references.py`](scripts/check_documentation_references.py): local Markdown links plus optional file-like code-span paths; emits stable machine-readable diagnostics and compatibility fields.
- [`scripts/check_markdown_structure.py`](scripts/check_markdown_structure.py): H1 count, heading jumps, ambiguous link text, fence closure/language, and missing Markdown image-alt warnings.
- [`scripts/package_skill.py`](scripts/package_skill.py): deterministic maintenance-only packaging with SHA-256 candidate/archive hashes, a durable `receipt_version` receipt, output alias preflight, staged validation, recovery-aware commit, and last-good preservation.

Helper results are mechanical evidence only; they do not prove semantic accuracy, runtime behavior, rendered accessibility, reader success, or editorial quality. [`evals/activation-scenarios.json`](evals/activation-scenarios.json) remains the frozen baseline activation coverage; [`evals/content-quality-v3-scenarios.json`](evals/content-quality-v3-scenarios.json) adds planned coverage for the v3 content/reader evidence contracts. Neither is behavioral evidence until actually executed.

## Workflow

1. **Freeze the review contract.** Record target, primary mode, content kind when material, audience/task, outcome, rubric identity, source set, evaluator/check identities, and applicable checks. For before/after claims, preserve an immutable baseline, freeze evaluator inputs, and capture a source snapshot of exact source bytes or pin an immutable source identity when mutable material evidence can affect the conclusion.
2. **Inspect source truth.** Read target docs and the smallest adjacent set needed to verify claims: scripts, validators, examples, configs, commands, contracts, or repository files.
3. **Run applicable checks.** Prefer frozen/target-native checks before generic helpers. Record exact commands/results. Missing execution is `not-run`, never pass.
4. **Create findings against stable criteria.** Use the review contract for schema, evidence labels, severity, deduplication, and ordering; separate observation from editorial judgment.
5. **Apply the smallest coherent edit.** Preserve public contracts, terminology, file names, command names, validator semantics, and ownership boundaries.
6. **Validate reader/task outcome only when evidence supports it.** Load `reader-task-validation.md` when task success, usability, or reader efficiency is claimed. Do not infer reader success from lint, source fidelity, or command execution.
7. **Re-run affected checks on final edited bytes.** Repair the diagnosed cause before adjacent cleanup.
8. **Bound repair.** Stop after two consecutive rounds that do not reduce the same objective error set; report the unresolved diagnostic.
9. **Freeze after pass.** After the final applicable checks pass, treat the exact edited bytes as the frozen candidate. Do not make unvalidated edits afterward; any later change invalidates affected evidence and requires revalidation.
10. **Report by evidence layer.** Keep mechanical, semantic/source-fidelity, runtime, reader/task-outcome, and editorial evidence distinct.

Use only `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked` when the review contract applies. A pass in one layer never implies another layer passed.

## Portability

The portable core is the Agent Skills package. Keep `agents/openai.yaml` optional, use package-local relative paths, and express execution as capabilities rather than host- or OS-specific commands. Do not require MCP or vendor-private APIs. Structural portability does not prove runtime behavior on every host.

## Boundaries

- Do not depend on MCP; use available file, repository, connector, or web access.
- Do not take ownership of full target-skill activation, hardening, benchmark scoring, package repair, or implementation code.
- Keep target `SKILL.md` compact; move branch-specific rubrics, examples, schemas, style guidance, and long procedures to conditional resources.
- Do not add documentation volume that worsens context economy.
- Do not document scripts/validators unless they exist and were inspected.
- Do not rewrite implementation code during documentation-only work unless explicitly requested.
- Do not force content into one taxonomy when the reader need is genuinely mixed or unclear.
- Do not turn readability scores, word counts, or style heuristics into hard correctness gates without a target-owned contract.
- Do not lower criteria, omit findings, delete semantic content, or relabel unavailable evidence to make a review appear cleaner.

## Stop conditions

Stop and report a blocker/gap when target docs are unavailable; required source truth cannot be inspected; claimed scripts, validators, commands, examples, outputs, or visual details cannot be verified; source-truth conflicts cannot be resolved in scope; a before/after comparison lost baseline/evaluator identity or material source identity; the request is actually full hardening, benchmarking, package repair, or implementation; restructuring would remove content with unknown ownership/consumers; or passing requires weakening criteria or hiding unavailable evidence.

## Output contract

For substantive reviews/edits include:

1. primary/secondary modes and content kind when material;
2. review-contract and rubric identity when loaded;
3. files inspected/changed;
4. material findings/improvements tied to criteria and evidence labels;
5. verification commands with `pass`, `fail`, or `not-run`;
6. separate mechanical, semantic/source-fidelity, runtime, reader/task-outcome, and editorial evidence;
7. source/evaluator identity for before/after claims when material;
8. risks, assumptions, unresolved gaps, blocked evidence;
9. only the next highest-value follow-up recommendation.

For direct edits, final edited bytes must pass every applicable executed mechanical check. Any later edit invalidates affected checks and requires revalidation.
