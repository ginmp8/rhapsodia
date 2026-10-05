---
name: documentation-quality
description: "use when the primary task is to review, edit, restructure, evaluate, or document human-facing technical documentation in a skill package or repository, including references, readmes, usage guides, scripts/validators, examples, tutorials, and troubleshooting. preserve source truth, contracts, terminology, accessibility, and context economy. do not use as the primary workflow for package-wide skill activation ownership, hardening, benchmarking, package repair, code implementation, presentation creation, or mcp-dependent work."
---

# Documentation Quality

## Purpose and activation boundary

Improve documentation against inspectable evidence. Target docs plus inspected scripts, validators, examples, configs, contracts, repository files, and executed command output are source truth. Never invent behavior, commands, results, ownership, reader success, or visual details. With the same target, evidence, mode, content intent, and rubric, repeated reviews should produce materially comparable findings even if editorial wording differs.

Use this skill when documentation quality is the primary deliverable. Route package-wide hardening/benchmarking/activation repair to the owning skill workflow, code implementation to a coding workflow, and presentation generation to a presentation workflow.

## Inputs and mode selection

Before changing target bytes or issuing a substantive review verdict, resolve or infer: target files/directories; primary mode; audience and reader task; requested outcome (`review`, `direct edits`, or both); inspectable source truth; target-native documentation checks; whether reader/task validation is requested or feasible; and whether a durable report/receipt is required. Resolve ambiguity only when target, audience/task, content purpose, or outcome would change the selected criteria or work.

| Request | Primary mode |
|---|---|
| Review `references/` | `reference-doc-review` |
| README/guide/main usage docs | `readme-review` |
| Scripts, commands, parameters, outputs, errors, validators | `script-documentation` |
| Examples/tutorials/scenarios | `example-improvement` |
| Markdown structure/accessibility | `markdown-accessibility` |
| Accuracy, completeness, flow, task success | `technical-content-evaluation` |
| Reorganize docs without duplication | `documentation-restructure` |
| Durable review report | `documentation-report` |

Add a secondary mode only when the request activates criteria not covered by the primary mode; one primary mode controls ordering and reporting. If document purpose changes obligations, resolve `content_kind` as `tutorial`, `how-to`, `reference`, `explanation`, `quickstart`, `troubleshooting`, `mixed`, or `unspecified`; never force intentionally mixed content into one type.

## Direct branch references

Load a branch only when its condition below applies. Every required Markdown branch is directly reachable here; do not depend on hidden Markdown-to-Markdown chains.

- [`references/review-contract.md`](references/review-contract.md) (`documentation-review-v2`): evidence labels, finding schema, severity, comparison identity, completion gates, bounded repair. Required for substantive reviews, validated edits, durable reports, or before/after claims.
- [`references/documentation-quality-rubric.md`](references/documentation-quality-rubric.md) (`documentation-quality-rubric-v3`): criteria and mode mapping.
- [`references/content-type-contracts.md`](references/content-type-contracts.md): purpose-specific obligations and mixed-content rules.
- [`references/reader-task-validation.md`](references/reader-task-validation.md): only for reader success, usability, task efficiency, or observed task-completion claims.
- [`references/language-and-global-readiness.md`](references/language-and-global-readiness.md): clarity, terminology, ambiguity, and conditional global-readiness review.
- [`references/markdown-accessibility-checklist.md`](references/markdown-accessibility-checklist.md): source/rendered accessibility boundaries.
- [`references/reference-file-patterns.md`](references/reference-file-patterns.md): Skill-reference structure, context economy, and restructure patterns.
- [`examples/skill-documentation-before-after.md`](examples/skill-documentation-before-after.md): concise rewrite calibration.
- [`assets/templates/documentation-review-report.md.template`](assets/templates/documentation-review-report.md.template): durable report shape.

## Execution and evidence contract

1. Freeze target, primary mode, content kind when it changes obligations, audience/task, outcome, rubric/source/evaluator identities, and applicable checks. For before/after claims, preserve an immutable baseline and material source identity.
2. Inspect target docs and only the adjacent source truth needed to verify their claims.
3. Run applicable checks in this precedence: exact user-supplied command; frozen approved-plan/review-contract command; target-native documentation validator/linter; bundled generic helper. Missing execution is `not-run`, never pass.
4. Create findings against stable criteria; separate observation from editorial judgment and apply the smallest coherent edit while preserving public contracts, terminology, filenames, command names, validator semantics, and ownership.
5. Claim reader/task success only from reader/task evidence; lint, source fidelity, or command execution alone cannot establish it.
6. Re-run affected checks on final edited bytes. Stop a repair branch after two consecutive rounds that do not reduce the same objective error set; preserve and report the unresolved diagnostic.
7. Freeze the exact candidate after the final applicable pass. Any later edit invalidates affected evidence and requires revalidation.
8. Report evidence layers separately: mechanical, semantic/source-fidelity, runtime, reader/task-outcome, editorial.

When the review contract applies, use only `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked`. A pass in one layer never implies another.

## Verification, boundaries, and stop rules

Resolve any available Python 3 launcher as `<PYTHON>`; do not require a vendor-specific executable, shell, MCP, or private API. Generic helpers are [`scripts/check_documentation_references.py`](scripts/check_documentation_references.py) and [`scripts/check_markdown_structure.py`](scripts/check_markdown_structure.py); [`scripts/package_skill.py`](scripts/package_skill.py) is maintenance-only packaging. Their results are mechanical evidence only. Planned eval files are not behavioral evidence until executed.

Keep `agents/openai.yaml` optional, package paths relative, and execution capability-based. Do not: own full target-skill hardening/benchmark/package repair; rewrite implementation code unless explicitly requested; document uninspected scripts/validators; bloat `SKILL.md` or references; force a taxonomy; turn readability/word-count/style heuristics into correctness gates without a target contract; weaken criteria, hide findings, delete semantic content, or relabel missing evidence to obtain a pass.

Stop and report a blocker/gap when target docs or required source truth are unavailable; claimed commands/artifacts/outputs/visuals cannot be verified; source conflicts cannot be resolved in scope; before/after identity is lost; the required change is package-wide hardening/benchmark/package repair or implementation code; restructuring may remove content with unknown consumers; or success requires weakening criteria or hiding unavailable evidence.

## Output contract

For substantive reviews/edits report: primary/secondary modes and content kind when used; loaded review-contract/rubric identity; files inspected/changed; material findings/improvements tied to criteria and evidence labels; verification commands as `pass`, `fail`, or `not-run`; evidence layers separately; source/evaluator identity for before/after claims; risks/assumptions/gaps/blocked evidence; and only the next highest-value follow-up. For direct edits, final bytes must pass every applicable executed mechanical check; later edits require revalidation.
