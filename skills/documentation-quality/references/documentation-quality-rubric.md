# Documentation quality rubric

Rubric identity: `documentation-quality-rubric-v2`

Use this rubric to review, rewrite, or evaluate technical documentation in Skill packages and repositories. Apply only criteria relevant to the selected mode. For stable evidence labels, severity rules, finding shape, ordering, and completion gates, also load `review-contract.md`.

## Mode-to-criterion map

| Mode | Primary criteria |
|---|---|
| `reference-doc-review` | DQ-01, DQ-02, DQ-03, DQ-06, DQ-07, DQ-08 |
| `readme-review` | DQ-01, DQ-02, DQ-03, DQ-04, DQ-07, DQ-08 |
| `script-documentation` | DQ-01, DQ-02, DQ-04, DQ-05, DQ-08 |
| `example-improvement` | DQ-01, DQ-02, DQ-04, DQ-07 |
| `markdown-accessibility` | DQ-03 plus `markdown-accessibility-checklist.md` |
| `technical-content-evaluation` | DQ-01 through DQ-08 as applicable |
| `documentation-restructure` | DQ-02, DQ-03, DQ-06, DQ-07, DQ-08 |
| `documentation-report` | Criteria activated by the reviewed modes plus the review-contract output rules |

## Evaluation criteria

### DQ-01 - Source fidelity and technical accuracy

Good documentation matches the actual package or repository.

Check that:

- described files, directories, scripts, validators, commands, flags, templates, examples, and outputs exist;
- instructions match the current command interface and file layout;
- examples use real names and realistic inputs;
- claims about validation, packaging, test coverage, compatibility, or measured quality are backed by inspected evidence;
- unsupported or unverifiable claims are marked as gaps or assumptions.

Failure patterns include promising a nonexistent command, describing uninspected validator behavior, claiming completeness while required artifacts are absent, or relying on stale prose instead of current source truth.

### DQ-02 - Audience and task fit

Good documentation makes the intended reader successful at the intended task.

Check that:

- the audience is clear: maintainer, agent, developer, reviewer, operator, or end user;
- prerequisites are explicit when they affect execution;
- the document starts with the reader's goal rather than a taxonomy dump;
- advanced details are separated from the first successful path;
- domain terms are preserved and clarified only when ambiguity would block the task.

### DQ-03 - Structure and navigability

Good documentation is easy to scan and use out of order.

Check that:

- title and headings describe the document's purpose;
- sections progress coherently from purpose to usage, rules, examples, validation, and troubleshooting when applicable;
- long references include a compact contents section when it materially improves navigation;
- related constraints are grouped rather than repeated;
- local links are descriptive and point to real resources.

Use `scripts/check_markdown_structure.py` for the mechanical subset when execution is available. Editorial information architecture remains a review judgment.

### DQ-04 - Actionability and examples

Good documentation gives enough concrete detail to execute without guesswork.

Check that:

- examples show realistic inputs and outputs;
- steps include verification points where failure is likely;
- examples demonstrate the recommended path before edge cases;
- examples avoid fake secrets, invented APIs, and unsupported boilerplate;
- before/after examples explain why the after state is better.

### DQ-05 - Script and validator documentation

Use this criterion for `script-documentation` and docs that mention deterministic tooling.

Document or verify:

- script or validator path;
- purpose and when to run it;
- required inputs, flags, environment assumptions, and defaults;
- outputs, side effects, exit behavior, generated files, and error handling;
- representative command examples;
- limitations and cases that remain manual.

If a script, validator, fixture, or command is mentioned but absent, record the missing artifact. Do not create a fictional interface description.

### DQ-06 - Skill-specific context economy

Good Skill documentation improves execution without bloating always-loaded instructions.

Check that:

- `SKILL.md` contains activation, routing, workflow, boundaries, and output contract rather than branch-specific detail;
- long rubrics, checklists, examples, schemas, and templates live in conditional resources;
- reference files are loaded only when needed and linked from the control plane;
- duplicated guidance is consolidated;
- documentation explains only what changes execution or reader success.

### DQ-07 - Completeness without over-documentation

Good documentation covers the real path and likely failure path, then stops.

Prefer adding documentation when it reduces repeated explanation, prevents common misuse, clarifies a fragile contract, or improves verification.

Avoid adding documentation when it repeats self-evident material, teaches generic concepts unrelated to the target, duplicates an already-clear source, or adds maintenance burden without execution value.

### DQ-08 - Maintainability and drift control

Good documentation is easy to keep aligned with the package.

Check that:

- source-of-truth files are named when useful;
- generated files and durable docs are not confused;
- version-specific or environment-specific claims are scoped;
- known gaps are explicit and actionable;
- broad claims such as `always`, `complete`, or `fully validated` are used only when evidence supports them;
- commands and paths most likely to drift are verified against current source truth.

## Review discipline

- Separate factual observation from editorial judgment.
- Use the same rubric identity for baseline and candidate when making before/after claims.
- Treat unused criteria as `not-applicable`, not failed.
- Use the review contract for severity rather than inventing per-run labels.
- Prefer one root-cause finding over many duplicate symptoms when the repair is the same.

## Review questions

Ask these silently while reviewing:

1. What task should this document make easier?
2. What is the source of truth for each technical claim?
3. Which claims are measured, observed, supplied, inferred, planned, or blocked?
4. What belongs in `SKILL.md`, references, examples, or templates?
5. Which single edit most improves reader success without unnecessary context?
6. Which evidence layer remains unverified after the edit?
