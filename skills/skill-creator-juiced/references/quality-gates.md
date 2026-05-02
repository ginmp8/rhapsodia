# Quality Gates

Use these gates before claiming a skill is ready.

## Structural Gates

- exactly one root `SKILL.md` for the package;
- frontmatter has `name` and `description`;
- name is lowercase hyphen-case and matches package intent;
- description states what the skill does and when to use it;
- `../agents/openai.yaml` exists for ChatGPT packages;
- referenced local files exist;
- no scaffold markers or unfinished placeholders remain outside template files;
- no caches, old zips, generated reports, or secrets are included.

## Activation Gates

- valid activation examples exist or are planned;
- non-activation examples exist for adjacent domains;
- ambiguous examples define when to ask, proceed, or hand off;
- description is specific enough to avoid false positives and broad enough to avoid common false negatives;
- boundaries and stop conditions are visible.

## Architecture Gates

- one operational role or an explicit router decision explains the package;
- modes share vocabulary, inputs, outputs, evidence, and validation;
- branch-specific detail lives in references, not the control plane;
- every important resource has a declared use;
- scripts are used for deterministic work, not ornamental complexity;
- assets are output materials, not hidden instructions.

## Content Gates

- instructions are imperative and actionable;
- workflow order is clear;
- defaults are preferred over menus;
- examples calibrate style or format;
- output contract is auditable;
- limitations and assumptions are visible;
- no validation, benchmark, or production-readiness claim is unsupported.

## Code and Script Gates

- added or changed scripts have safe command interfaces;
- a deterministic package builder exists for `skill.zip` delivery;
- scripts avoid unsafe shell invocation, path traversal, broad deletes, and untrusted archive extraction;
- scripts have at least a smoke test or syntax check;
- dependencies are minimal and justified;
- failures are reported without pretending success.

## Final Package Gate

A package can be delivered only when:

- local quality gate passes or remaining warnings are explicitly accepted;
- platform/package validator passes;
- `skill.zip` exists at the reported path;
- archive size is below the upload limit;
- final response distinguishes executed validation from planned validation.
