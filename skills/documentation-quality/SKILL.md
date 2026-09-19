---
name: documentation-quality
description: use when asked to create, review, reorganize, evaluate, or improve technical documentation inside skill packages or repositories, including reference files, readmes, usage guides, script and validator documentation, examples, tutorials, and human-oriented technical guides. improves clarity, structure, accessibility, technical accuracy, examples, and flow while preserving domain terms, contracts, source truth, scope boundaries, and context economy. do not use for full target-skill activation ownership, hardening, benchmarking, code implementation, or mcp-dependent workflows.
---

# Documentation Quality

## Core rule

Improve documentation against inspectable evidence. Treat target files, scripts, validators, examples, READMEs, contracts, and executed command output as source truth. Never invent behavior, commands, validation results, ownership boundaries, or visual details.

Reproducibility means repeated reviews of the same target, evidence, mode, and rubric version should produce materially comparable findings and validation decisions. Editorial wording may still vary.

## Required inputs

Resolve or infer before material edits:

- target files or directories;
- primary documentation mode and any secondary modes;
- intended audience;
- requested outcome: review, direct edits, or both;
- source truth available for verification;
- whether a durable report or machine-readable receipt is required.

If target, audience, or outcome ambiguity would materially change the work, resolve it before broad rewriting.

## Mode selection

| User request | Mode |
|---|---|
| Review files under `references/` | `reference-doc-review` |
| Review a README, guide, or main usage document | `readme-review` |
| Document scripts, commands, parameters, outputs, errors, or validator behavior | `script-documentation` |
| Improve examples, before/after cases, tutorials, or usage scenarios | `example-improvement` |
| Improve Markdown headings, links, lists, tables, alt text, and scanability | `markdown-accessibility` |
| Evaluate accuracy, completeness, flow, and reader task success | `technical-content-evaluation` |
| Propose a cleaner documentation layout without duplication | `documentation-restructure` |
| Produce a durable review report with changes, rationale, risks, and gaps | `documentation-report` |

Use multiple modes only when the request genuinely spans them. Keep one primary mode for ordering criteria and reporting.

## Progressive loading

Load only what the active mode needs:

- [`references/review-contract.md`](references/review-contract.md): evidence labels, finding schema, severity, ordering, completion gates, before/after fairness, and bounded repair.
- [`references/documentation-quality-rubric.md`](references/documentation-quality-rubric.md): versioned quality criteria and mode mapping.
- [`references/markdown-accessibility-checklist.md`](references/markdown-accessibility-checklist.md): Markdown accessibility and readability.
- [`references/reference-file-patterns.md`](references/reference-file-patterns.md): Skill reference files, context economy, and restructure patterns.
- [`assets/templates/documentation-review-report.md.template`](assets/templates/documentation-review-report.md.template): durable human-readable review report.
- [`examples/skill-documentation-before-after.md`](examples/skill-documentation-before-after.md): compact rewrite calibration.

Load `review-contract.md` for substantive reviews, validated direct edits, or durable reports.

## Verification helpers

- `scripts/check_documentation_references.py`: local Markdown links and optional file-like code-span paths. Emits stable machine-readable diagnostics and retains legacy `missing`/`skipped` fields.
- `scripts/check_markdown_structure.py`: objective Markdown structure checks including H1 count, heading-level jumps, ambiguous link text, fenced-code closure, and missing fence language tags.
- `scripts/package_skill.py`: maintenance-only skill validation and packaging; not part of normal documentation review.

Helper output is mechanical evidence only. It cannot prove semantic accuracy, runtime behavior, reader success, or editorial quality.

`evals/activation-scenarios.json` is planned coverage. Do not report scenario metrics as measured unless those scenarios were executed and captured.

## Workflow

1. **Freeze the review contract.** Record target, primary mode, audience, requested outcome, rubric identity, source set, and applicable mechanical checks. Before/after comparisons must use the same target scope and criteria.
2. **Inspect source truth.** Read the target docs and the smallest adjacent source set needed to verify claims: scripts, validators, examples, configs, commands, contracts, or repository files.
3. **Run applicable mechanical checks.** Capture exact commands and results when execution is available. Missing execution is `not-run`, never a pass.
4. **Create findings against stable criteria.** Use the finding schema, evidence labels, severity rules, deduplication, and ordering from `review-contract.md`. Separate factual observation from editorial judgment.
5. **Apply the smallest coherent edit.** Preserve public contracts, terminology, file names, command names, validator semantics, and ownership boundaries.
6. **Re-run the same applicable checks on the edited bytes.** Repair the diagnosed cause before adjacent cleanup.
7. **Bound repair.** Stop after two consecutive rounds that do not reduce the same objective error set and report the unresolved diagnostic.
8. **Report evidence by layer.** Keep mechanical, semantic/source-fidelity, runtime, and editorial evidence distinct.

Use only these evidence labels when the review contract applies: `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked`. A pass in one evidence layer never implies another layer passed.

## Boundaries

- Do not depend on MCP. Use file, repository, connector, or web access available in the environment.
- Do not take ownership of full target-skill activation, hardening, benchmark scoring, package repair, or code implementation.
- Keep target `SKILL.md` files compact; put branch-specific rubrics, examples, schemas, and long procedures in conditional resources.
- Do not add documentation volume that worsens context economy.
- Do not document scripts or validators as present unless they exist and were inspected.
- Do not rewrite implementation code during documentation-only work unless explicitly requested.
- Do not lower criteria, omit findings, delete semantic content, or relabel unavailable evidence to make a review appear cleaner.

## Stop conditions

Stop and report a blocker or gap when:

- target documentation is unavailable or unreadable;
- required source truth cannot be inspected;
- a claimed script, validator, command, example, output, or visual detail cannot be found or verified;
- conflicting source-truth artifacts cannot be resolved within scope;
- the requested work is actually full skill hardening, benchmarking, package repair, or implementation;
- a restructure would remove content whose ownership or consumers are unknown;
- passing would require weakening selected criteria or hiding unavailable evidence.

## Output contract

For substantive reviews or edits, include:

1. primary and secondary mode(s);
2. review-contract and rubric identity when loaded;
3. files inspected and changed;
4. material findings or improvements tied to criteria and evidence labels;
5. verification commands with `pass`, `fail`, or `not-run` status;
6. mechanical, semantic/source-fidelity, runtime, and editorial evidence kept separate;
7. risks, assumptions, unresolved gaps, and blocked evidence;
8. only the next highest-value follow-up recommendation.

For direct edits, completion requires that the final edited bytes pass every applicable executed mechanical check. Any later edit invalidates affected checks and requires revalidation.
