# Documentation quality rubric

Rubric identity: `documentation-quality-rubric-v3`

Use this rubric to review, rewrite, or evaluate technical documentation in Skill packages and repositories. Apply only criteria relevant to the selected mode and content kind. For stable evidence labels, severity rules, finding shape, ordering, comparison identity, and completion gates, also load `review-contract.md`. When document purpose changes the obligation, load `content-type-contracts.md`.

## Mode-to-criterion map

| Mode | Primary criteria |
|---|---|
| `reference-doc-review` | DQ-01, DQ-02, DQ-03, DQ-06, DQ-07, DQ-08, DQ-09 |
| `readme-review` | DQ-01, DQ-02, DQ-03, DQ-04, DQ-07, DQ-08, DQ-09 |
| `script-documentation` | DQ-01, DQ-02, DQ-04, DQ-05, DQ-08, DQ-09 |
| `example-improvement` | DQ-01, DQ-02, DQ-04, DQ-07, DQ-09 |
| `markdown-accessibility` | DQ-03, DQ-09 plus `markdown-accessibility-checklist.md` |
| `technical-content-evaluation` | DQ-01 through DQ-10 as applicable |
| `documentation-restructure` | DQ-02, DQ-03, DQ-06, DQ-07, DQ-08, DQ-09 |
| `documentation-report` | Criteria activated by the reviewed modes plus the review-contract output rules |

DQ-10 is conditional: activate it when the request or claim includes reader success, usability, task efficiency, or observed task completion.

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

### DQ-02 - Audience, task, and content-purpose fit

Good documentation serves the intended reader at the intended moment.

Check that:

- the audience is clear: maintainer, agent, developer, reviewer, operator, or end user;
- the reader's goal or information need is clear enough to choose the right level of detail;
- prerequisites are explicit when they affect execution;
- the document starts with the reader's goal rather than a taxonomy dump;
- advanced details are separated from the first successful path;
- the content kind is inferred only when it materially changes the review and mixed content remains allowed.

Use `content-type-contracts.md` for type-specific obligations.

### DQ-03 - Structure, findability, and navigability

Good documentation is easy to enter, scan, look up, and use out of order when its content type allows it.

Check that:

- title and headings describe the document's purpose;
- a reader can identify the correct entry point for the task or information need;
- sections progress coherently from purpose to usage, rules, examples, validation, and troubleshooting when applicable;
- long references include a compact contents section when it materially improves navigation;
- related constraints are grouped rather than repeated;
- local links are descriptive and point to real resources;
- task-oriented pages connect to deeper reference/explanation without duplicating them unnecessarily;
- detail pages preserve a path back to the surrounding context when the documentation set needs it.

Use `scripts/check_markdown_structure.py` for the mechanical subset when execution is available. Editorial information architecture and findability remain review judgment unless task/navigation evidence was actually collected.

### DQ-04 - Actionability, examples, and failure paths

Good documentation gives enough concrete detail to execute without guesswork.

Check that:

- examples show realistic inputs and outputs;
- examples are identified by their real contract when material: illustrative, partial, copy-paste-ready, executable, or expected-output;
- executable claims are run when safe/available or reported `not-run`/`blocked`;
- steps include verification points where failure is likely;
- common failures include diagnosis, recovery/workaround, and verification when evidence exists;
- examples demonstrate the recommended path before edge cases;
- examples avoid fake secrets, invented APIs, and unsupported boilerplate;
- before/after examples explain why the after state is better.

An illustrative snippet is not defective merely because it is not executable. The defect is claiming stronger executability than the evidence supports.

### DQ-05 - Script and validator documentation

Use this criterion for `script-documentation` and docs that mention deterministic tooling.

Document or verify:

- script or validator path;
- purpose and when to run it;
- required inputs, flags, environment assumptions, and defaults;
- outputs, side effects, exit behavior, generated files, and error handling;
- representative command examples;
- limitations and cases that remain manual.

Prefer the target's own documented validator/linter when it exists. Bundled generic helpers are fallback mechanical evidence, not a replacement for stronger repository-native checks.

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

Prefer adding documentation when it reduces repeated explanation, prevents common misuse, clarifies a fragile contract, improves recovery, or improves verification.

Avoid adding documentation when it repeats self-evident material, teaches generic concepts unrelated to the target, duplicates an already-clear source, or adds maintenance burden without execution value.

### DQ-08 - Maintainability, lifecycle, and drift control

Good documentation is easy to keep aligned with the package over time.

Check that:

- source-of-truth files are named when useful;
- generated files and durable authored docs are not confused;
- generated documentation identifies its source/refresh mechanism when applicable;
- version-specific or environment-specific claims are scoped;
- deprecation state and supported version scope are explicit when they affect the reader;
- durable product docs avoid unnecessary time-relative terms such as `new`, `currently`, or `latest` when those words will age without adding meaning;
- known gaps and known issues are explicit and actionable;
- broad claims such as `always`, `complete`, or `fully validated` are used only when evidence supports them;
- commands and paths most likely to drift are verified against current source truth;
- source-to-doc synchronization or ownership is clear when drift risk is high.

### DQ-09 - Language clarity and terminology consistency

Good documentation minimizes interpretation cost without weakening domain precision.

Check that:

- terminology is consistent and aligned with source truth;
- conditions, pronouns, modal words, and scope qualifiers are unambiguous;
- distinct technical claims are not compressed into confusing compound sentences;
- acronyms are introduced when audience knowledge cannot be assumed;
- style heuristics do not override technically necessary terminology;
- global-readiness rules from `language-and-global-readiness.md` are applied only when relevant to the audience.

Readability scores and word counts are supporting heuristics, not hard correctness gates unless the target explicitly defines them.

### DQ-10 - Reader and task outcome evidence

Activate this criterion only when the review claims reader success, usability, task efficiency, or reduced confusion.

Check that:

- the reader profile, goal, starting state, and success condition are explicit enough to interpret the claim;
- before/after comparisons use the same frozen scenario/evaluator inputs when feasible;
- actual task completion, blockers, wrong turns, lookup effort, time, or feedback are reported only when observed/measured/supplied;
- editorial predictions about likely reader impact remain `inferred`;
- a pass in mechanical, semantic, or runtime-command layers is never presented as reader-success proof.

Load `reader-task-validation.md` for the detailed evidence boundary.

## Review discipline

- Separate factual observation from editorial judgment.
- Use the same review-contract/rubric identities for baseline and candidate when making comparable before/after claims; otherwise re-baseline explicitly.
- Treat unused criteria as `not-applicable`, not failed.
- Use the review contract for severity rather than inventing per-run labels.
- Prefer one root-cause finding over many duplicate symptoms when the repair is the same.
- Do not force taxonomy purity when mixed content better serves the reader.

## Review questions

Ask these silently while reviewing:

1. What task or information need should this document satisfy?
2. Which content purpose is dominant, mixed, or intentionally unspecified?
3. What is the source of truth for each technical claim?
4. Which claims are measured, observed, supplied, inferred, planned, or blocked?
5. What belongs in `SKILL.md`, references, examples, or templates?
6. Which single edit most improves reader success without unnecessary context?
7. Which evidence layer remains unverified after the edit?
