# Source Integration

Use this reference when a prompt must be created or improved from documentation, URLs, repositories, code files, standards, product docs, or multiple source artifacts.

## Source Hierarchy

Prefer sources in this order unless the user states otherwise:

1. user-provided constraints and examples;
2. official documentation and maintained repositories;
3. repository-local README, contributing guides, tests, and examples;
4. internal docs or project conventions available through connected sources;
5. reputable secondary sources;
6. inferred best practices.

When sources conflict, prefer the most authoritative, current, and task-specific source. State unresolved conflicts when the final prompt depends on them.

## Extraction Checklist

Extract only information that changes prompt execution:

- required inputs and outputs;
- build, deploy, test, or operational commands;
- domain definitions and naming conventions;
- constraints, edge cases, and prohibited actions;
- version-specific behavior;
- examples and anti-examples;
- source-specific success criteria;
- required citations or traceability.

Avoid copying source material wholesale. Convert it into concise, actionable prompt instructions.

## Research Integration Pattern

When sources are used, include a concise source note unless the user asks for prompt-only output:

- sources inspected;
- key requirements extracted;
- conflicts resolved;
- assumptions made;
- source gaps that affect confidence.

In the final prompt, include source rules only when future executions need them. Do not include one-time research notes inside a reusable prompt unless they will help the model perform future tasks.

## Repository and Codebase Prompts

For prompts based on a codebase:

- inspect README, package files, project configuration, tests, and representative implementation files;
- infer conventions from repeated patterns, not isolated examples;
- distinguish required rules from observed preferences;
- avoid hardcoding paths that are likely to change unless the prompt is repository-specific;
- add tool-use instructions only for tools that the executing agent actually has.

## Citation and Evidence

When the user asks for citations or the prompt will be used in a research-heavy workflow, instruct the target model to cite sources close to the claims they support. Require explicit uncertainty when sources are unavailable or insufficient.
