# Specialist Passbook

Every complete optimization run must execute, apply by checklist, or explicitly classify each pass below.

Status values:

- `pass`: the specialist or equivalent check ran and gates passed.
- `fail`: the specialist or equivalent check ran and gates failed.
- `blocked`: required evidence or execution is unavailable.
- `not-run`: intentionally skipped; explain why.
- `not-applicable`: pass has no relevant artifact; explain evidence.
- `applied-by-checklist`: specialist could not be directly invoked, but this passbook checklist was applied.
- `planned`: scenario or metric was designed but not executed.

## Pass Order

### 1. skill-creator-juiced

Purpose: provide production-ready skill-design governance and escalation for major redesign. Use when the target optimization reveals that the skill should be substantially redesigned, converted to modes/router behavior, split, or rebuilt with a stricter package architecture.

Required output:

- architecture escalation decision;
- specialist sequence confirmation;
- quality gate expectations;
- rationale for continuing as optimization versus major redesign.

Checklist:

- preserve the target skill's purpose and language needs;
- keep `SKILL.md` as control plane;
- move long branch detail to direct references;
- do not fabricate benchmark, validation, or readiness claims;
- require package quality gates before delivery.

### 2. skill-improver

Purpose: coordinate objective, evaluator freeze, hypotheses, accept/reject decisions, and final closure.

Required output:

- objective;
- metric contract;
- hypothesis list;
- accepted/rejected decision records.

Checklist:

- state baseline before mutation;
- use one bounded hypothesis per patch batch;
- reject changes that miss delta, fail gates, or alter blocked files;
- record untested claims as proposals.

### 3. skill-benchmark

Purpose: establish initial and final maturity score or readiness report.

Required output:

- score or gate report;
- maturity risks;
- comparison baseline/final when measured.

Checklist:

- separate structural score from behavioral score;
- do not claim precision, recall, robustness, or maturity without evidence;
- if score is saturated, add auxiliary signal such as unresolved-risk count, token count, scenario coverage, or gate count.

### 4. skill-harness

Purpose: create or run repeatable scenarios.

Required scenario groups:

- activation;
- non-activation;
- ambiguous;
- edge;
- regression;
- output contract.

Checklist:

- freeze scenarios before candidate patch;
- preserve expected outputs unless benchmark design is explicitly in scope;
- record planned scenarios separately from executed outcomes.

### 5. skill-package-architecture-review

Purpose: decide package structure.

Checklist:

- determine unified skill, modes, router, split, or stop;
- verify one coherent operational responsibility;
- keep `SKILL.md` as control plane;
- move branch detail to direct references;
- verify resources have declared use.

### 6. context-architect

Purpose: map dependency and cross-file impact.

Use when the target includes scripts, validators, generated outputs, repo references, or many resource files.

Checklist:

- map affected files;
- find imports and script consumers;
- identify ripple effects;
- define safe implementation sequence;
- avoid unrelated repository changes.

### 7. skill-prompt-and-activation-review

Purpose: refine activation and boundaries.

Checklist:

- frontmatter description names target artifacts and concrete triggers;
- adjacent non-triggers are visible;
- ambiguous requests have ask/proceed/stop rules;
- output contract is auditable;
- stop conditions block unsafe or unsupported work.

### 8. prompt-architect

Purpose: refine complex prompt bodies or agent instructions.

Use when the skill contains reusable prompts, long instructions, model-facing templates, or agent prompts.

Checklist:

- preserve user intent;
- state success criteria;
- remove vague behavior words;
- include examples only when they calibrate behavior;
- avoid executing the target task when the task is to improve the prompt.

### 9. skill-consistency-repair

Purpose: repair contradictions and integration gaps.

Checklist:

- compare `SKILL.md` with references and scripts;
- ensure local links resolve;
- remove stale claims;
- align output contract with examples;
- mark unsupported claims as assumptions or remove them.

### 10. documentation-quality

Purpose: improve human-facing and model-facing documentation.

Checklist:

- references have clear titles and scoped purpose;
- examples are short and realistic;
- script usage is documented when scripts exist;
- claims are source-backed or framed as design decisions;
- docs do not duplicate `SKILL.md` unnecessarily.

### 11. karpathy-guidelines

Purpose: keep code and technical artifacts simple and testable.

Checklist:

- scripts do one thing;
- command-line options are explicit;
- error messages are useful;
- no overbuilt framework for simple validation;
- tests or smoke checks exist for modified scripts.

### 12. security-and-governance-review

Purpose: prevent unsafe or over-authorized behavior.

Checklist:

- no secrets or credentials in package;
- no broad deletes or unsafe shell execution;
- no sensitive logging;
- archive extraction and filesystem writes are scoped;
- tool authority and user confirmation boundaries are clear;
- residual risks are recorded.

### 13. skill-testing-and-validation

Purpose: run checks and record outcomes.

Checklist:

- run structure validation;
- run local link checks;
- run modified scripts once or syntax-check them;
- run package validation when packaging;
- record pass/fail commands exactly.

### 14. skill-cleanup-and-simplification

Purpose: remove excess after integration is understood.

Checklist:

- remove caches, old zips, generated reports, duplicate text, and unused scaffold;
- classify files before deletion;
- consolidate repeated rules;
- keep useful templates and references that the workflow uses.

### 15. skill-token-efficient

Purpose: reduce token cost while preserving semantics.

Checklist:

- run only after behavior and contracts are stable;
- preserve triggers, exclusions, workflow, safety, validation, and output sections;
- compress `SKILL.md` conservatively;
- re-run validation immediately after compression.

### 16. skill-hardening

Purpose: final readiness and package maturity.

Checklist:

- final inventory passes;
- all support files are integrated;
- no generated noise remains;
- validators and package checks pass;
- package scope is exactly the final target skill.

### 17. final skill-benchmark

Purpose: confirm final state and delta.

Checklist:

- compare against baseline;
- distinguish measured score from judgment;
- list residual risks and next improvement hypothesis.

### 18. final skill-improver closure

Purpose: close the optimization run.

Checklist:

- accept/reject hypotheses;
- record files changed;
- report final gates;
- give rollback path when available;
- provide `skill.zip` only when present and validated.
