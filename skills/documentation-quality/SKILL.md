---
name: documentation-quality
description: use when asked to create, review, reorganize, evaluate, or improve technical documentation inside skill packages or repositories, including reference files, readmes, usage guides, script and validator documentation, examples, tutorials, and human-oriented technical guides. improves clarity, structure, accessibility, technical accuracy, examples, and flow while preserving domain terms, contracts, source truth, scope boundaries, and context economy. do not use for full target-skill activation ownership, hardening, benchmarking, code implementation, or mcp-dependent workflows.
---

# Documentation Quality

## Core rule

Improve documentation against inspectable evidence. Target files, scripts, validators, examples, READMEs, contracts, and executed command output are source truth. Never invent behavior, commands, validation results, ownership boundaries, or visual details. Repeated reviews using the same target, evidence, mode, and rubric should produce materially comparable findings; editorial wording may vary.

## Required inputs

Resolve or infer before material edits:

- target files/directories;
- primary mode and any secondary modes;
- intended audience;
- requested outcome: review, direct edits, or both;
- source truth available for verification;
- whether a durable report or machine-readable receipt is required.

Resolve ambiguity first only when target, audience, or outcome materially changes the work.

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

## Progressive loading

Load only what the active mode needs:

- [`references/review-contract.md`](references/review-contract.md): evidence labels, finding schema, severity, ordering, completion gates, fair comparison, bounded repair.
- [`references/documentation-quality-rubric.md`](references/documentation-quality-rubric.md): versioned quality criteria and mode mapping.
- [`references/markdown-accessibility-checklist.md`](references/markdown-accessibility-checklist.md): Markdown accessibility/readability.
- [`references/reference-file-patterns.md`](references/reference-file-patterns.md): Skill references, context economy, restructure patterns.
- [`assets/templates/documentation-review-report.md.template`](assets/templates/documentation-review-report.md.template): durable review shape.
- [`examples/skill-documentation-before-after.md`](examples/skill-documentation-before-after.md): rewrite calibration.

Load the linked review contract for substantive reviews, validated direct edits, or durable reports.

## Verification helpers

Resolve an available Python 3 launcher and denote it `<PYTHON>`. Do not require a particular executable name, shell, installation path, or vendor-private API. Bundled helpers use only the Python standard library.

- [`scripts/check_documentation_references.py`](scripts/check_documentation_references.py): local Markdown links plus optional file-like code-span paths; emits stable machine-readable diagnostics and existing compatibility fields.
- [`scripts/check_markdown_structure.py`](scripts/check_markdown_structure.py): H1 count, heading jumps, ambiguous link text, fence closure, and fence-language checks.
- [`scripts/package_skill.py`](scripts/package_skill.py): deterministic maintenance-only packaging, not normal documentation review.

Helper results are mechanical evidence only; they do not prove semantic accuracy, runtime behavior, reader success, or editorial quality. [`evals/activation-scenarios.json`](evals/activation-scenarios.json) is planned coverage until actually executed.

## Workflow

1. **Freeze the review contract.** Record target, primary mode, audience, outcome, rubric identity, source set, and applicable checks. Use the same scope/criteria for before/after comparisons.
2. **Inspect source truth.** Read target docs and the smallest adjacent set needed to verify claims: scripts, validators, examples, configs, commands, contracts, or repository files.
3. **Run applicable mechanical checks.** Record exact commands/results. Missing execution is `not-run`, never pass.
4. **Create findings against stable criteria.** Use the linked review contract for schema, evidence labels, severity, deduplication, and ordering; separate observation from editorial judgment.
5. **Apply the smallest coherent edit.** Preserve public contracts, terminology, file names, command names, validator semantics, and ownership boundaries.
6. **Re-run the same checks on final edited bytes.** Repair the diagnosed cause before adjacent cleanup.
7. **Bound repair.** Stop after two consecutive rounds that do not reduce the same objective error set; report the unresolved diagnostic.
8. **Report by evidence layer.** Keep mechanical, semantic/source-fidelity, runtime, and editorial evidence distinct.

Use only `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked` when the review contract applies. A pass in one layer never implies another layer passed.

## Portability

The portable core is the Agent Skills package. Keep `agents/openai.yaml` optional, use package-local relative paths, and express execution as capabilities rather than host- or OS-specific commands. Structural portability does not prove runtime behavior on every host.

## Boundaries

- Do not depend on MCP; use available file, repository, connector, or web access.
- Do not take ownership of full target-skill activation, hardening, benchmark scoring, package repair, or code implementation.
- Keep target `SKILL.md` compact; move branch-specific rubrics, examples, schemas, and long procedures to conditional resources.
- Do not add documentation volume that worsens context economy.
- Do not document scripts/validators unless they exist and were inspected.
- Do not rewrite implementation code during documentation-only work unless explicitly requested.
- Do not lower criteria, omit findings, delete semantic content, or relabel unavailable evidence to make a review appear cleaner.

## Stop conditions

Stop and report a blocker/gap when target docs are unavailable; required source truth cannot be inspected; claimed scripts, validators, commands, examples, outputs, or visual details cannot be verified; source-truth conflicts cannot be resolved in scope; the request is actually full hardening, benchmarking, package repair, or implementation; restructuring would remove content with unknown ownership/consumers; or passing requires weakening criteria or hiding unavailable evidence.

## Output contract

For substantive reviews/edits include:

1. primary/secondary modes;
2. review-contract and rubric identity when loaded;
3. files inspected/changed;
4. material findings/improvements tied to criteria and evidence labels;
5. verification commands with `pass`, `fail`, or `not-run`;
6. separate mechanical, semantic/source-fidelity, runtime, and editorial evidence;
7. risks, assumptions, unresolved gaps, blocked evidence;
8. only the next highest-value follow-up recommendation.

For direct edits, final edited bytes must pass every applicable executed mechanical check. Any later edit invalidates affected checks and requires revalidation.
