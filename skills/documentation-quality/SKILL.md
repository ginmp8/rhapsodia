---
name: documentation-quality
description: use when asked to create, review, reorganize, evaluate, or improve technical documentation inside skill packages or repositories, including reference files, readmes, usage guides, script and validator documentation, examples, tutorials, and human-oriented technical guides. improves clarity, structure, accessibility, technical accuracy, examples, and flow while preserving domain terms, contracts, source truth, scope boundaries, and context economy. do not use for full target-skill activation ownership, hardening, benchmarking, code implementation, or mcp-dependent workflows.
---

# Documentation Quality

## Core rule

Improve documentation against inspectable evidence. Treat target files, scripts, validators, examples, READMEs, and existing contracts as the source of truth. Do not invent behavior, commands, validation results, or ownership boundaries.


## Required inputs

Before editing or reviewing documentation, resolve or infer:

- target files or directories to inspect;
- selected documentation mode;
- intended audience and requested output format;
- source truth available for verification, such as adjacent Skill files, README files, scripts, validators, examples, or repository files;
- whether the user expects direct edits, a review report, or both.

## Verification helpers

Use `scripts/check_documentation_references.py` when filesystem access is available and the task needs local Markdown link checks or optional file-like code-span checks. Treat its output as structural evidence only; semantic accuracy still requires document review.

Use `scripts/package_skill.py` only as a maintenance utility for validating and packaging a skill folder as `skill.zip`; do not treat it as part of the documentation-review workflow.

Use `evals/activation-scenarios.json` as planned activation and boundary coverage for this Skill. Do not report scenario metrics as measured unless the scenarios were actually executed and results were captured.

## Mode selection

| User request | Mode |
|---|---|
| Review files under `references/` | `reference-doc-review` |
| Review a README, guide, or main usage document | `readme-review` |
| Document scripts, commands, parameters, outputs, errors, or validator behavior | `script-documentation` |
| Improve examples, before/after cases, tutorials, or usage scenarios | `example-improvement` |
| Improve Markdown headings, links, lists, tables, alt text, and scanability | `markdown-accessibility` |
| Evaluate technical accuracy, completeness, flow, and reader task success | `technical-content-evaluation` |
| Propose a cleaner documentation layout without duplication | `documentation-restructure` |
| Produce a durable review report with changes, rationale, risks, and gaps | `documentation-report` |

Use multiple modes only when the user request clearly spans them. Name the selected mode in the final report.

## Workflow

1. Identify the documentation target and intended audience. Infer the mode from the request when not explicit.
2. Inspect relevant source truth before editing: target docs, adjacent `SKILL.md`, referenced files, scripts, validators, examples, commands, configs, or repository files.
3. Load only the needed supporting resource:
   - `references/documentation-quality-rubric.md` for clarity, precision, completeness, examples, script docs, and technical-content evaluation.
   - `references/markdown-accessibility-checklist.md` for Markdown accessibility and readability passes.
   - `references/reference-file-patterns.md` for Skill reference files, context economy, and documentation restructure.
   - `assets/templates/documentation-review-report.md.template` when a durable report is requested.
   - `examples/skill-documentation-before-after.md` when examples or rewrite patterns are needed.
4. Apply the smallest documentation change that improves execution, comprehension, or trust. Preserve domain terminology, public contracts, file names, command names, and validator semantics.
5. Verify documentation claims against files that exist. When a claim cannot be verified, mark it as a gap instead of presenting it as fact.
6. Report changes, rationale, risks, remaining gaps, and validation evidence.

## Boundaries

- Do not depend on MCP. Use normal file, repository, connector, or web access available in the current environment.
- Do not take ownership of full target-skill activation, boundaries, hardening, benchmark scoring, or package repair. Hand off to a dedicated skill-hardening, benchmark, harness, improver, or consistency workflow when the user asks for those deliverables.
- Do not move detailed rubrics, long examples, schemas, or exhaustive explanations into the target `SKILL.md`. Keep `SKILL.md` as a compact control plane and put conditional detail in `references/`.
- Do not create documentation volume that worsens context economy. Prefer concise docs that help the next execution step.
- Do not document scripts or validators as present unless they exist. If missing, record the missing artifact as a documentation gap.
- Do not rewrite code while performing documentation quality work unless the user explicitly requests code edits separately.


## Stop conditions

Stop and report a blocker or gap when:

- the target documentation is unavailable or unreadable;
- a requested edit requires source truth that is not present and cannot be inspected;
- a document claims a script, validator, command, example, or output exists but the artifact cannot be found;
- the user asks for full skill hardening, benchmark scoring, package repair, or code implementation rather than documentation quality work;
- the requested change would add broad reference material that does not improve execution or reader success.

## Output contract

For reviews or edits, include:

1. selected mode or modes;
2. files inspected and files changed;
3. key improvements grouped by clarity, structure, accuracy, accessibility, examples, and context economy when applicable;
4. verification performed, including file-existence checks for mentioned scripts, validators, examples, commands, and local links;
5. risks, assumptions, and unresolved gaps;
6. follow-up recommendations limited to the next highest-value documentation change.
