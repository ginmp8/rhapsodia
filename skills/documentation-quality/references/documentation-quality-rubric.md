# Documentation quality rubric

Use this rubric to review, rewrite, or evaluate technical documentation in Skill packages and repositories. Apply only the dimensions relevant to the user's requested mode.

## Evaluation dimensions

### 1. Source fidelity and technical accuracy

Good documentation matches the actual package or repository.

Check that:

- described files, directories, scripts, validators, commands, flags, templates, examples, and outputs exist;
- instructions match the current command interface and file layout;
- examples use real names and realistic inputs;
- claims about validation, packaging, test coverage, compatibility, or measured quality are backed by inspected evidence;
- unsupported or unverifiable claims are marked as gaps or assumptions.

Failure patterns:

- promising a command that does not exist;
- describing validator output without running or inspecting the validator;
- saying a package is complete while local examples are missing;
- summarizing outdated behavior because only a README was read.

### 2. Audience and task fit

Good documentation makes the target reader successful at the intended task.

Check that:

- the audience is clear: maintainer, agent, developer, reviewer, operator, or end user;
- prerequisites are explicit when they affect execution;
- the document starts with the reader's goal, not a taxonomy dump;
- advanced details are separated from the first successful path;
- domain terms are preserved and briefly clarified only when ambiguity would block the task.

### 3. Structure and navigability

Good documentation is easy to scan and easy to use out of order.

Check that:

- the title and headings describe the document's purpose;
- sections progress from purpose to usage, rules, examples, validation, and troubleshooting when applicable;
- long reference files include a compact table of contents;
- related constraints are grouped together instead of repeated across sections;
- local links are descriptive and point to real files.

### 4. Actionability and examples

Good documentation gives enough concrete detail to execute without guesswork.

Check that:

- examples show realistic inputs and expected outputs;
- steps include verification points where failure is likely;
- examples demonstrate the recommended path, not only edge cases;
- examples avoid fake secrets, fake package names, invented APIs, or generic boilerplate;
- before/after examples explain why the after version is better.

### 5. Script and validator documentation

Use this dimension for `script-documentation` and docs that mention deterministic tooling.

Document or verify:

- script or validator path;
- purpose and when to run;
- required inputs, flags, environment assumptions, and defaults;
- outputs, side effects, exit behavior, generated files, and error handling;
- representative command examples;
- limitations and cases that remain manual.

If a script, validator, fixture, or command is mentioned but absent, do not create a fictional description. Record the missing artifact and recommend either adding the artifact or removing the claim.

### 6. Skill-specific context economy

Good Skill documentation improves execution without bloating always-loaded instructions.

Check that:

- `SKILL.md` contains activation, workflow, boundaries, and routing only;
- detailed rubrics, long checklists, examples, schemas, and report templates live in `references/`, `examples/`, or `assets/templates/`;
- reference files are loaded conditionally and linked directly from `SKILL.md`;
- duplicated guidance is consolidated;
- documentation explains only what changes agent behavior or reader success.

### 7. Completeness without over-documentation

Good documentation covers the real path and the likely failure path, then stops.

Prefer adding documentation when it:

- reduces repeated explanation across future runs;
- prevents a common misuse or unsafe claim;
- clarifies a fragile command, artifact, contract, or decision;
- improves verification of real outputs.

Avoid adding documentation when it:

- repeats self-evident instructions;
- describes generic Markdown or programming concepts unrelated to the target;
- duplicates a source file that is already clear;
- introduces maintenance burden without helping execution.

### 8. Maintainability and drift control

Good documentation is easy to keep aligned with the package.

Check that:

- source-of-truth files are named when helpful;
- generated files and durable docs are not confused;
- version-specific or environment-specific claims are scoped;
- known gaps are explicit and actionable;
- documentation avoids broad claims such as "always", "complete", or "fully validated" unless evidence supports them.

## Severity guide

| Severity | Use when | Recommended action |
|---|---|---|
| blocker | The doc instructs the reader to run a missing or dangerous command, or makes unsupported completion/validation claims | Fix before release or mark as gap |
| high | The doc is likely to mislead execution, break a workflow, or hide missing artifacts | Correct claim, add evidence, or restructure |
| medium | The doc is usable but unclear, incomplete, duplicated, or hard to scan | Edit for clarity and flow |
| low | The issue affects polish, consistency, or minor accessibility | Batch with adjacent improvements |

## Review questions

Ask these silently while reviewing:

1. What task should this document make easier?
2. What is the source of truth for each technical claim?
3. Which claims did I verify, and which remain assumptions?
4. What should stay in `SKILL.md`, what belongs in `references/`, and what belongs in `assets/templates/`?
5. Which single edit most improves reader success without adding unnecessary context?
